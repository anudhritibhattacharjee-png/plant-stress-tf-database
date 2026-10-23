#!/usr/bin/env python3
"""PhytoStress TF Atlas — Full Curated Dataset Importer.

Imports all 63 reconciled transcription factor records into the normalized
relational database (SQLite/PostgreSQL) using SQLAlchemy ORM.

Authoritative reference documents:
- docs/data_mapping_report.md
- docs/data_quality_report.md
- docs/data_dictionary.md
- docs/full_dataset_reconciliation.md
"""

import os
import sys
import json
import re
import hashlib
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import SessionLocal, Base, engine
from backend.app.models import (
    TFFamily,
    Plant,
    TranscriptionFactor,
    StressCondition,
    TFStressAssociation,
    TFIdentifier,
    ResearchPaper,
    TFPaperAssociation,
    TargetGene,
    TFTargetAssociation,
    Pathway,
    TFPathwayAssociation,
    ImportAudit,
)


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def clean_string(val: Optional[str]) -> Optional[str]:
    """Strips whitespace and converts empty strings to None."""
    if val is None:
        return None
    val = str(val).strip()
    return val if val else None


def clean_title(title_raw: Optional[str]) -> str:
    """Strips enclosing quotes (single, double, smart quotes) and whitespace."""
    if not title_raw:
        return ""
    t = str(title_raw).strip()
    t = re.sub(r'^[“"\'\s]+|[”"\'\s]+$', '', t)
    return t.strip()


def extract_clean_doi(doi_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Extracts clean DOI identifier and canonical HTTP URL."""
    if not doi_str:
        return None, None
    raw = str(doi_str).strip()
    clean = raw
    for prefix in ["https://doi.org/", "http://doi.org/", "https://link.springer.com/"]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break
    clean = clean.strip()
    url = raw if raw.startswith("http") else f"https://doi.org/{clean}"
    return clean, url


def get_or_create_family(session: Session, raw_family: str) -> TFFamily:
    """Retrieves or creates a normalized TFFamily."""
    fam_name = clean_string(raw_family) or "Unknown"
    fam = session.query(TFFamily).filter(TFFamily.name == fam_name).first()
    if not fam:
        fam = TFFamily(name=fam_name)
        session.add(fam)
        session.flush()
    return fam


def get_or_create_plant(session: Session, raw_plant: str) -> Plant:
    """Retrieves or creates a normalized Plant entity."""
    display = clean_string(raw_plant) or "Unknown"
    plant = session.query(Plant).filter(Plant.display_name == display).first()
    if plant:
        return plant

    common = display
    scientific = None
    tax_id = None

    # Parse parenthetical scientific binomial or comments
    # e.g., "Tomato (Solanum lycopersicum)"
    m = re.match(r"^([^(]+)(?:\(([^;)]+)(?:;\s*([^)]+))?\))?$", display)
    if m:
        common = m.group(1).strip()
        if m.group(2):
            scientific = m.group(2).strip()

    # Known common-to-scientific mapping dictionary
    known_taxonomy = {
        "Tomato": ("Solanum lycopersicum", 4081),
        "Arabidopsis": ("Arabidopsis thaliana", 3702),
        "Arabidopsis thaliana": ("Arabidopsis thaliana", 3702),
        "Rice": ("Oryza sativa", 4530),
        "Rice (Oryza sativa)": ("Oryza sativa", 4530),
        "Wheat": ("Triticum aestivum", 4565),
        "Triticum aestivum (wheat)": ("Triticum aestivum", 4565),
        "Apple": ("Malus domestica", 3750),
        "Cotton": ("Gossypium hirsutum", 3635),
        "Cotton (Gossypium hirsutum)": ("Gossypium hirsutum", 3635),
        "Cotton (Gossypium hirsutum; functional test in Arabidopsis)": ("Gossypium hirsutum", 3635),
        "Soybean": ("Glycine max", 3847),
        "Soybean (Glycine max)": ("Glycine max", 3847),
        "Maize (Zea mays; functional test in Arabidopsis)": ("Zea mays", 4577),
        "Zea mays (maize)": ("Zea mays", 4577),
        "Potato (Solanum tuberosum; AtBBX21 used for functional analysis)": ("Solanum tuberosum", 4113),
        "Black poplar (Populus trichocarpa)": ("Populus trichocarpa", 3694),
        "Medicago truncatula": ("Medicago truncatula", 3880),
        "Birch": ("Betula pendula", 3505),
        "Brassica": ("Brassica napus", 3708),
        "Grape": ("Vitis vinifera", 29760),
        "Walnut": ("Juglans regia", 16719),
        "Watermelon": ("Citrullus lanatus", 3654),
        "Pepper": ("Capsicum annuum", 4072),
        "Ananas comosus (pineapple)": ("Ananas comosus", 4615),
        "O. taihangensis": ("Opisthopappus taihangensis", 160086),
        "Multiple plants": (None, None),
    }

    if display in known_taxonomy:
        scientific, tax_id = known_taxonomy[display]
    elif common in known_taxonomy:
        if not scientific:
            scientific, tax_id = known_taxonomy[common]

    plant = Plant(
        display_name=display,
        common_name=common,
        scientific_name=scientific,
        ncbi_taxonomy_id=tax_id
    )
    session.add(plant)
    session.flush()
    return plant


def get_or_create_paper(session: Session, record: Dict[str, Any]) -> ResearchPaper:
    """Retrieves or creates a ResearchPaper record with deduplication."""
    title = clean_title(record.get("Research paper "))
    journal = clean_string(record.get("Journal"))
    if journal in ["___", "—", "-"]:
        journal = None
    
    year_val = record.get("Year")
    year = None
    raw_citation = None
    if year_val is not None:
        raw_year_str = str(year_val).strip()
        raw_citation = f"Year: {raw_year_str}"
        y_match = re.search(r"\b(19\d\d|20\d\d)\b", raw_year_str)
        if y_match:
            year = int(y_match.group(1))
    
    doi, doi_url = extract_clean_doi(record.get("DOI Number"))

    query = session.query(ResearchPaper)
    if doi:
        paper = query.filter(ResearchPaper.doi == doi).first()
    else:
        paper = query.filter(ResearchPaper.title == title).first()

    if not paper:
        paper = ResearchPaper(
            title=title,
            journal=journal,
            year=year,
            doi=doi,
            doi_url=doi_url,
            raw_citation_text=raw_citation
        )
        session.add(paper)
        session.flush()
    return paper



def normalize_stresses(raw_stress: str) -> List[Tuple[str, str]]:
    """Maps composite and single stress descriptions into normalized stress conditions and categories."""
    clean = clean_string(raw_stress) or ""
    
    stress_mapping = {
        "Drought, cold, osmotic stress": [("Drought", "Abiotic"), ("Cold", "Abiotic"), ("Osmotic stress", "Abiotic")],
        "Drought, salt": [("Drought", "Abiotic"), ("Salt stress", "Abiotic")],
        "Drought and salt": [("Drought", "Abiotic"), ("Salt stress", "Abiotic")],
        "Salt and drought": [("Salt stress", "Abiotic"), ("Drought", "Abiotic")],
        "Salt, drought": [("Salt stress", "Abiotic"), ("Drought", "Abiotic")],
        "Salinity and drought": [("Salt stress", "Abiotic"), ("Drought", "Abiotic")],
        "Cold, salt, osmotic stress": [("Cold", "Abiotic"), ("Salt stress", "Abiotic"), ("Osmotic stress", "Abiotic")],
        "Drought, salt, cold, heat, oxidative stress": [("Drought", "Abiotic"), ("Salt stress", "Abiotic"), ("Cold", "Abiotic"), ("Heat", "Abiotic"), ("Oxidative stress", "Abiotic")],
        "Drought, osmotic and salt-associated stress": [("Drought", "Abiotic"), ("Osmotic stress", "Abiotic"), ("Salt stress", "Abiotic")],
        "Drought and oxidative stress": [("Drought", "Abiotic"), ("Oxidative stress", "Abiotic")],
        "Chilling/cold stress": [("Cold", "Abiotic")],
        "Cold stress": [("Cold", "Abiotic")],
        "Cold": [("Cold", "Abiotic")],
        "Drought": [("Drought", "Abiotic")],
        "Drought stress": [("Drought", "Abiotic")],
        "Moderate drought": [("Drought", "Abiotic")],
        "Heat": [("Heat", "Abiotic")],
        "Heat stress": [("Heat", "Abiotic")],
        "Salt": [("Salt stress", "Abiotic")],
        "Salt stress": [("Salt stress", "Abiotic")],
        "Salt / abiotic stress; broader biotic-stress regulation": [("Salt stress", "Abiotic"), ("Abiotic stress", "Abiotic"), ("Biotic stress", "Biotic")],
        "Abiotic stress": [("Abiotic stress", "Abiotic")],
        "Phosphorus deficiency": [("Phosphorus deficiency", "Nutrient")],
        "Nitrate": [("Nitrate stress", "Nutrient")],
        "Nitrate stress": [("Nitrate stress", "Nutrient")],
        "Nitrate response": [("Nitrate response", "Nutrient")],
        "Nitrogen stress": [("Nitrogen stress", "Nutrient")],
        "Nitrogen-use efficiency": [("Nitrogen-use efficiency", "Nutrient")],
        "Nitrate / nodulation": [("Nitrate response", "Nutrient"), ("Nodulation", "Nutrient")],
        "Nitrate / root response": [("Nitrate response", "Nutrient"), ("Root development", "Nutrient")],
        "Nitrate / seed germination": [("Nitrate response", "Nutrient"), ("Seed germination", "Nutrient")],
        "Nitrogen limitation / N metabolism": [("Nitrogen limitation", "Nutrient"), ("Nitrogen metabolism", "Nutrient")],
        "Nitrogen/nitrate availability": [("Nitrate availability", "Nutrient"), ("Nitrogen limitation", "Nutrient")],
        "Oxidative stress": [("Oxidative stress", "Abiotic")],
        "Botrytis cinerea infection": [("Botrytis cinerea infection", "Biotic")],
        "Verticillium wilt (Verticillium dahliae)": [("Verticillium wilt", "Biotic")]
    }

    if clean in stress_mapping:
        return stress_mapping[clean]

    # Fallback parsing
    parts = re.split(r",\s*|\s+and\s+|;\s*|\s*/\s*", clean)
    results = []
    for p in parts:
        p_c = p.strip()
        if p_c:
            results.append((p_c, "Abiotic"))
    return results


def link_stresses(session: Session, tf: TranscriptionFactor, raw_stress: str) -> List[StressCondition]:
    """Links normalized stress conditions to TF via junction table."""
    stress_defs = normalize_stresses(raw_stress)
    linked = []
    for s_name, s_type in stress_defs:
        cond = session.query(StressCondition).filter(StressCondition.stress_name == s_name).first()
        if not cond:
            cond = StressCondition(stress_name=s_name, stress_type=s_type)
            session.add(cond)
            session.flush()

        assoc = session.query(TFStressAssociation).filter(
            TFStressAssociation.tf_id == tf.id,
            TFStressAssociation.stress_id == cond.id
        ).first()
        if not assoc:
            session.add(TFStressAssociation(
                tf_id=tf.id,
                stress_id=cond.id,
                specific_effect=tf.regulatory_effect
            ))
        linked.append(cond)
    session.flush()
    return linked


def parse_and_link_identifiers(session: Session, tf: TranscriptionFactor, record: Dict[str, Any]) -> List[TFIdentifier]:
    """Parses and stores external accessions and locus identifiers without data loss or fabrication."""
    raw_id = clean_string(record.get("Uniprot Accession ID/Valid Gene ID")) or ""
    id_type = clean_string(record.get("Identifier Type")) or ""
    uniprot_pattern = re.compile(r"\b([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})\b")
    created = []

    # Case: Empty / Missing (e.g. Record 24 MADS-box family)
    if not raw_id:
        tf.is_verified = False
        tf.notes = "Family-level synthesis review; no single gene accession applicable."
        return created

    # Case: Explicitly Not verified
    if "Not verified" in raw_id:
        tf.is_verified = False
        tf.notes = "Accession explicitly noted as 'Not verified' in literature source."

        ncbi_m = re.search(r"NCBI\s+Gene\s+(\d+)", id_type, re.IGNORECASE)
        if ncbi_m:
            ncbi_ident = TFIdentifier(
                tf_id=tf.id,
                identifier_type="NCBI Gene",
                identifier_value=ncbi_m.group(1),
                verification_status="Not verified",
                raw_supplied_text=raw_id,
                is_primary=False
            )
            session.add(ncbi_ident)
            created.append(ncbi_ident)

        sym_m = re.search(r"Gene symbol\s+([A-Za-z0-9_\-]+)", id_type)
        if sym_m:
            sym_ident = TFIdentifier(
                tf_id=tf.id,
                identifier_type="Gene symbol",
                identifier_value=sym_m.group(1),
                verification_status="Not verified",
                raw_supplied_text=raw_id,
                is_primary=False
            )
            session.add(sym_ident)
            created.append(sym_ident)
        elif "(" in id_type:
            paren_m = re.search(r"\(([A-Za-z0-9_\-]+)\)", id_type)
            if paren_m:
                sym_ident = TFIdentifier(
                    tf_id=tf.id,
                    identifier_type="Gene symbol",
                    identifier_value=paren_m.group(1),
                    verification_status="Not verified",
                    raw_supplied_text=raw_id,
                    is_primary=False
                )
                session.add(sym_ident)
                created.append(sym_ident)

        session.flush()
        return created

    # Case: Author doubts (Record 36)
    if "not sure whether the proteins are transcription factors" in raw_id:
        tf.is_verified = False
        tf.notes = "Author note: not sure whether the proteins are transcription factors or not."
        u_matches = uniprot_pattern.findall(raw_id)
        for u in u_matches:
            c_ident = TFIdentifier(
                tf_id=tf.id,
                identifier_type="UniProtKB",
                identifier_value=u,
                verification_status="Candidate / Uncertain",
                raw_supplied_text=raw_id,
                is_primary=False
            )
            session.add(c_ident)
            created.append(c_ident)
        session.flush()
        return created

    # Case: IWGSC Wheat Gene IDs (TraesCS...)
    traes_matches = re.findall(r"TraesCS[0-9A-Z]+", raw_id)
    if traes_matches:
        for idx, t in enumerate(traes_matches):
            ident = TFIdentifier(
                tf_id=tf.id,
                identifier_type="IWGSC Wheat Gene ID",
                identifier_value=t,
                verification_status="Verified",
                raw_supplied_text=raw_id,
                is_primary=(idx == 0)
            )
            session.add(ident)
            created.append(ident)
        session.flush()
        return created

    # Case: Solyc Gene IDs (Solyc...)
    solyc_matches = re.findall(r"Solyc\d{2}g\d{6}", raw_id)
    if solyc_matches:
        for idx, s in enumerate(solyc_matches):
            ident = TFIdentifier(
                tf_id=tf.id,
                identifier_type="Sol Genomics Network",
                identifier_value=s,
                verification_status="Verified",
                raw_supplied_text=raw_id,
                is_primary=(idx == 0)
            )
            session.add(ident)
            created.append(ident)
        session.flush()
        return created

    # Case: Birch Gene IDs (BPChr...)
    bp_matches = re.findall(r"BPChr\d+G\d+", raw_id)
    if bp_matches:
        for idx, bp in enumerate(bp_matches):
            ident = TFIdentifier(
                tf_id=tf.id,
                identifier_type="Birch Gene ID",
                identifier_value=bp,
                verification_status="Verified",
                raw_supplied_text=raw_id,
                is_primary=(idx == 0)
            )
            session.add(ident)
            created.append(ident)
        session.flush()
        return created

    # Multi-component parsing: UniProt, TAIR, NCBI Gene, Loci
    u_matches = uniprot_pattern.findall(raw_id)
    tair_matches = re.findall(r"AT[1-5]G\d{5}", raw_id, re.IGNORECASE)
    ncbi_matches = re.findall(r"NCBI\s+Gene\s+(\d+)", raw_id, re.IGNORECASE)
    if not ncbi_matches:
        ncbi_matches = re.findall(r"NCBI\s+Gene\s+(\d+)", id_type, re.IGNORECASE)

    loc_matches = re.findall(r"LOC_Os\d+g\d+", raw_id)
    gb_matches = [g for g in re.findall(r"\b([A-Z]{1,2}\d{5,6})\b", raw_id) if g not in u_matches]
    maize_matches = re.findall(r"Zm\d+d\d+|GRMZM\d+G\d+", raw_id)
    cotton_matches = re.findall(r"Gh_[A-Z0-9]+", raw_id)
    pine_matches = re.findall(r"Aco\d+", raw_id)

    if u_matches:
        primary_candidate = "Q84NC5" if "Q84NC5" in u_matches else u_matches[0]
        for u in u_matches:
            ident = TFIdentifier(
                tf_id=tf.id,
                identifier_type="UniProtKB",
                identifier_value=u,
                verification_status="Verified",
                raw_supplied_text=raw_id,
                is_primary=(u == primary_candidate)
            )
            session.add(ident)
            created.append(ident)

    for t in tair_matches:
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="TAIR",
            identifier_value=t.upper(),
            verification_status="Verified",
            raw_supplied_text=raw_id,
            is_primary=(len(u_matches) == 0)
        )
        session.add(ident)
        created.append(ident)

    for n in ncbi_matches:
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="NCBI Gene",
            identifier_value=n,
            verification_status="Verified",
            raw_supplied_text=raw_id,
            is_primary=False
        )
        session.add(ident)
        created.append(ident)

    for l in loc_matches:
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="MSU Rice Locus",
            identifier_value=l,
            verification_status="Verified",
            raw_supplied_text=raw_id,
            is_primary=False
        )
        session.add(ident)
        created.append(ident)

    for g in gb_matches:
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="GenBank",
            identifier_value=g,
            verification_status="Verified",
            raw_supplied_text=raw_id,
            is_primary=False
        )
        session.add(ident)
        created.append(ident)

    for m in maize_matches:
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="MaizeGDB",
            identifier_value=m,
            verification_status="Verified",
            raw_supplied_text=raw_id,
            is_primary=False
        )
        session.add(ident)
        created.append(ident)

    for c in cotton_matches:
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="Cotton Gene Model",
            identifier_value=c,
            verification_status="Verified",
            raw_supplied_text=raw_id,
            is_primary=False
        )
        session.add(ident)
        created.append(ident)

    for p in pine_matches:
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="Pineapple Locus ID",
            identifier_value=p,
            verification_status="Verified",
            raw_supplied_text=raw_id,
            is_primary=False
        )
        session.add(ident)
        created.append(ident)

    # Fallback if unparsed raw identifier remains
    if not created and raw_id:
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="Curated Identifier",
            identifier_value=raw_id,
            verification_status="Verified",
            raw_supplied_text=raw_id,
            is_primary=True
        )
        session.add(ident)
        created.append(ident)

    session.flush()
    return created


def parse_and_link_targets_and_pathways(session: Session, tf: TranscriptionFactor, plant: Plant, raw_targets: str):
    """Parses target genes and physiological pathways and links them to TF."""
    clean = clean_string(raw_targets) or ""
    if not clean:
        return

    # Specific biological target and pathway mappings for key studies
    target_symbols = []
    pathway_names = []

    # Gene symbol extraction pattern: capitalized symbols like SlSOS1, WRKY33, DREB2A, etc.
    genes_found = re.findall(r"\b([A-Z][a-zA-Z0-9_\-]{2,15})\b", clean)
    ignore_words = {
        "D-mannose", "L-galactose", "SOS", "Na+", "ABA", "MeJA", "SA", "PEG", "ROS",
        "RNAi", "ChIP-seq", "DAP-seq", "RNA-seq", "EMSA", "T-DNA", "BiFC", "Y2H",
        "Co-IP", "LCI", "CRT", "DRE", "NRE", "PB1", "Pi", "K+", "NO", "JA", "HSPs",
        "E-box", "Pro239Leu", "Ser314", "MAR", "MARs", "H3K9me2", "DNA-binding",
        "Overexpression", "Down-regulation", "Multiple", "Common", "Primary"
    }

    # Custom targets for verified studies
    target_rule_map = {
        1: (["SlSOS1"], ["Ascorbate recycling", "SOS-mediated Na+ homeostasis"]),
        2: (["Na+ excretion"], ["ABA/MeJA salt-signalling", "Stomatal regulation"]),
        3: (["ANAC069"], ["Auxin signalling", "Salt and drought response"]),
        5: (["CBF", "DREB2A", "ZAT10", "ZAT12"], ["Osmoprotection", "Oxidative-stress metabolism"]),
        6: ([], ["Flowering-time network", "Abiotic-stress response"]),
        7: (["MdAPX3", "MdACO1", "MdTGD2", "MdAPL3"], ["Hydraulic water transport", "Photosynthetic drought response"]),
        8: ([], ["ROS scavenging", "Cellular protection"]),
        11: (["GolS"], ["Raffinose oligosaccharide biosynthesis"]),
        13: (["JrGRAS2"], ["Heat-shock response", "Antioxidant pathways"]),
        14: (["OsACS1"], ["Ethylene biosynthesis", "Root meristem development"]),
        15: (["OsAMT1;1", "OsAMT1;3", "OsAMT2;1", "OsAMT4;1"], ["Ammonium uptake", "Nitrogen assimilation"]),
        20: (["MT-1-4b"], ["Anther ROS-scavenging"]),
        21: ([], ["Nitrate accumulation", "Root development"]),
        22: (["OsIAA14"], ["Auxin signalling", "Nitrate-auxin crosstalk"]),
        31: (["CLE35"], ["SUNN-CRA2 nodulation signalling", "Nitrate-dependent symbiotic control"]),
        32: (["CLE35"], ["SUNN-CRA2 nodulation signalling"]),
        37: (["OsNR", "OsABA8ox1"], ["Nitrate reductase pathway", "NO signalling"]),
        39: (["CYP707A2"], ["ABA catabolism", "Seed germination"]),
        40: (["GmNIN1a", "GmENOD40-1"], ["Nodulation signalling"]),
        41: (["GmSALT3", "GmMYB84", "GmNCED3", "GmRbohB"], ["ABA signalling", "Ion homeostasis"]),
        45: (["ESE1"], ["Ethylene signalling", "SOS2-dependent salt response"]),
        46: (["CHS", "F3H", "CHI"], ["Flavonoid biosynthesis"]),
        47: (["NCED3", "ABI1", "ABI2", "ABI4", "ABI5", "RD22", "RD29A", "KIN1"], ["ABA signalling"]),
        48: (["RD29A", "SOS1", "ABF4", "CBL1"], ["Osmotic/salt signalling", "ROS protection"]),
        49: (["GhGT-3b_A04"], ["Salicylic acid defence", "Verticillium resistance"]),
        50: (["OsMAPK3"], ["Antioxidant enzymatic cascade"]),
        51: (["OsGPX1"], ["Glutathione peroxidase antioxidant defence"]),
        52: (["PAL"], ["Phenylpropanoid biosynthesis"]),
        53: (["DREB2A", "SAP12", "SNRK2-5"], ["ABA signalling", "Stomatal regulation"]),
        54: (["CBL4", "SOS3", "CBL10", "SCaBP8"], ["SOS pathway", "Na+ homeostasis"]),
        55: (["PIP2;8", "ABI3", "ABI4", "ABI5"], ["Stomatal closure", "ABA signalling"]),
        58: ([], ["Oxidative-stress response", "E-box transcriptional network"]),
        59: (["SlMYB30", "SlMYBL2", "SlPIF4", "SlHAT1", "SlIWS1", "SlREF6"], ["Brassinosteroid signalling"]),
        60: (["CDK8", "SUVH2", "SUVH9"], ["H3K9me2 chromatin repression", "Salt tolerance regulation"]),
        62: (["HSFA2", "HSC70.3"], ["Heat-shock response"]),
        63: (["WRKY33", "ORA59", "PAD3"], ["JA/ethylene defence", "Camalexin biosynthesis"])
    }

    if tf.id in target_rule_map:
        target_symbols, pathway_names = target_rule_map[tf.id]
    else:
        # Generic pathway term extraction
        pathway_names = [p.strip() for p in re.split(r";\s*|\s+and\s+", clean) if len(p.strip()) > 3]

    # Link targets
    for gene_sym in target_symbols:
        if gene_sym in ignore_words or not gene_sym:
            continue
        target = session.query(TargetGene).filter(
            TargetGene.gene_symbol == gene_sym,
            TargetGene.plant_id == plant.id
        ).first()
        if not target:
            target = TargetGene(gene_symbol=gene_sym, plant_id=plant.id)
            session.add(target)
            session.flush()

        assoc = session.query(TFTargetAssociation).filter(
            TFTargetAssociation.tf_id == tf.id,
            TFTargetAssociation.target_gene_id == target.id
        ).first()
        if not assoc:
            session.add(TFTargetAssociation(
                tf_id=tf.id,
                target_gene_id=target.id,
                regulation_mode="Reported downstream target"
            ))

    # Link pathways
    for p_name in pathway_names:
        p_clean = p_name.strip()
        if not p_clean or len(p_clean) < 3:
            continue
        pathway = session.query(Pathway).filter(Pathway.pathway_name == p_clean).first()
        if not pathway:
            pathway = Pathway(pathway_name=p_clean)
            session.add(pathway)
            session.flush()

        assoc = session.query(TFPathwayAssociation).filter(
            TFPathwayAssociation.tf_id == tf.id,
            TFPathwayAssociation.pathway_id == pathway.id
        ).first()
        if not assoc:
            session.add(TFPathwayAssociation(
                tf_id=tf.id,
                pathway_id=pathway.id
            ))

    session.flush()


def run_full_import(
    json_path: str = "data/raw/prototype_63_records.json",
    session: Optional[Session] = None,
    dry_run: bool = False,
    reset_existing: bool = True
) -> Dict[str, Any]:
    """Imports all 63 curated transcription factor records into the database.
    
    Returns a dictionary of execution results and statistics.
    """
    should_close_session = False
    if session is None:
        session = SessionLocal()
        should_close_session = True

    try:
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Source records file not found at: {json_path}")

        file_hash = compute_sha256(json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        if len(records) != 63:
            raise ValueError(f"Expected exactly 63 source records, got {len(records)}")

        # Check existing records in database
        existing_count = session.query(TranscriptionFactor).count()
        if existing_count == 63 and not reset_existing:
            print("[DUPLICATE-SAFETY] All 63 records are already present in the database.")
            print("[DUPLICATE-SAFETY] Skipping re-import to guarantee idempotent duplicate-safety.")
            return {
                "status": "SKIPPED_EXISTING",
                "message": "All 63 records already exist in database. Import skipped safely.",
                "records_processed": 63,
                "records_inserted": 0,
                "file_hash": file_hash
            }

        # If reset_existing is True, clear previous test import tables safely within the transaction
        if reset_existing and existing_count > 0:
            print(f"[RESET] Resetting {existing_count} existing test records for clean 63-record full dataset ingestion...")
            # Truncate/delete existing records in cascade inside transaction (rolled back in dry-run, committed in real run)
            session.query(TFPathwayAssociation).delete()
            session.query(TFTargetAssociation).delete()
            session.query(TFStressAssociation).delete()
            session.query(TFPaperAssociation).delete()
            session.query(TFIdentifier).delete()
            session.query(TranscriptionFactor).delete()
            session.query(TargetGene).delete()
            session.query(Pathway).delete()
            session.query(StressCondition).delete()
            session.query(ResearchPaper).delete()
            session.query(Plant).delete()
            session.query(TFFamily).delete()
            session.query(ImportAudit).delete()
            session.flush()


        stats = {
            "records_processed": 0,
            "records_inserted": 0,
            "plants_count": 0,
            "families_count": 0,
            "papers_count": 0,
            "stresses_count": 0,
            "stress_associations_count": 0,
            "identifiers_count": 0,
            "targets_count": 0,
            "pathways_count": 0,
            "unverified_count": 0,
            "imported_tfs": []
        }

        for idx, rec in enumerate(records, start=1):
            stats["records_processed"] += 1
            raw_tf_name = clean_string(rec.get("TF / TF family"))
            raw_stress = clean_string(rec.get("Stress condition"))
            raw_targets = clean_string(rec.get("Key Target(s) / Pathway"))
            
            # Resolve Family & Plant
            family = get_or_create_family(session, rec.get("Standardized TF Family"))
            plant = get_or_create_plant(session, rec.get("Plant"))
            
            # Dataset origin
            source_dataset = "curated_excel"
            if idx == 30 or idx == 36:
                source_dataset = "html_supplement"
                
            # Create TranscriptionFactor
            tf = TranscriptionFactor(
                tf_name=raw_tf_name,
                family_id=family.id,
                plant_id=plant.id,
                regulatory_effect=clean_string(rec.get("Regulatory Effect")),
                mechanism_description=clean_string(rec.get("How it regulates stress")),
                validation_system=clean_string(rec.get("Validation System")),
                evidence_summary=clean_string(rec.get("Evidence Type")),
                raw_supplied_tf=raw_tf_name,
                raw_stress=raw_stress,
                raw_targets=raw_targets,
                source_dataset=source_dataset,
                source_row_index=idx,
                is_verified=True,
                notes=None
            )
            session.add(tf)
            session.flush()
            stats["records_inserted"] += 1

            # Paper & Association
            paper = get_or_create_paper(session, rec)
            p_assoc = session.query(TFPaperAssociation).filter(
                TFPaperAssociation.tf_id == tf.id,
                TFPaperAssociation.paper_id == paper.id
            ).first()
            if not p_assoc:
                session.add(TFPaperAssociation(
                    tf_id=tf.id,
                    paper_id=paper.id,
                    evidence_notes=clean_string(rec.get("Evidence Type"))
                ))
                session.flush()

            # Stresses & Junctions
            linked_stresses = link_stresses(session, tf, raw_stress)

            # Identifiers
            created_ids = parse_and_link_identifiers(session, tf, rec)
            if not tf.is_verified:
                stats["unverified_count"] += 1

            # Targets & Pathways
            parse_and_link_targets_and_pathways(session, tf, plant, raw_targets)

            stats["imported_tfs"].append({
                "db_id": tf.id,
                "tf_name": tf.tf_name,
                "plant": plant.common_name,
                "family": family.name,
                "is_verified": tf.is_verified,
                "stresses": [s.stress_name for s in linked_stresses],
                "identifiers_count": len(created_ids),
                "doi": paper.doi
            })

        # Query exact counts
        stats["tfs_count"] = session.query(TranscriptionFactor).count()
        stats["plants_count"] = session.query(Plant).count()
        stats["families_count"] = session.query(TFFamily).count()
        stats["papers_count"] = session.query(ResearchPaper).count()
        stats["paper_associations_count"] = session.query(TFPaperAssociation).count()
        stats["stresses_count"] = session.query(StressCondition).count()
        stats["stress_associations_count"] = session.query(TFStressAssociation).count()
        stats["identifiers_count"] = session.query(TFIdentifier).count()
        stats["targets_count"] = session.query(TargetGene).count()
        stats["target_associations_count"] = session.query(TFTargetAssociation).count()
        stats["pathways_count"] = session.query(Pathway).count()
        stats["pathway_associations_count"] = session.query(TFPathwayAssociation).count()

        # Create ImportAudit
        audit = ImportAudit(
            source_name=json_path,
            source_type="JSON",
            source_hash=file_hash,
            records_processed=stats["records_processed"],
            records_inserted=stats["records_inserted"],
            records_updated=0,
            status="SUCCESS",
            validation_summary=json.dumps({
                "imported_count": stats["records_inserted"],
                "table_counts": {
                    "transcription_factors": stats["tfs_count"],
                    "plants": stats["plants_count"],
                    "tf_families": stats["families_count"],
                    "research_papers": stats["papers_count"],
                    "stress_conditions": stats["stresses_count"],
                    "tf_identifiers": stats["identifiers_count"],
                    "target_genes": stats["targets_count"],
                    "pathways": stats["pathways_count"]
                }
            }),
            error_information=None
        )
        session.add(audit)
        session.flush()
        stats["audits_count"] = session.query(ImportAudit).count()

        if dry_run:
            print("[DRY-RUN] Full import simulation successful. Rolling back transaction without committing.")
            session.rollback()
            stats["status"] = "DRY_RUN_SUCCESS"
        else:
            session.commit()
            stats["status"] = "SUCCESS"
            print(f"[SUCCESS] Successfully committed {stats['records_inserted']} TF records and associated relational entities.")

        return stats

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Import failed with error: {e}. Transaction rolled back.")
        try:
            audit_fail = ImportAudit(
                source_name=json_path,
                source_type="JSON",
                records_processed=0,
                records_inserted=0,
                records_updated=0,
                status="FAILED",
                error_information=str(e)
            )
            session.add(audit_fail)
            session.commit()
        except Exception:
            pass
        raise e
    finally:
        if should_close_session:
            session.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PhytoStress TF Atlas Full Data Importer")
    parser.add_argument("--json", default="data/raw/prototype_63_records.json", help="Path to source JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without committing")
    parser.add_argument("--no-reset", action="store_true", help="Do not clear existing test records before import")
    args = parser.parse_args()

    print(f"Starting full curated data import from '{args.json}' (dry_run={args.dry_run}, reset={not args.no_reset})...")
    res = run_full_import(json_path=args.json, dry_run=args.dry_run, reset_existing=not args.no_reset)
    print(json.dumps(res, indent=2, default=str))
