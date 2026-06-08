# State of the Art: CRISPR/Cas9 and Next-Generation Gene Editing for Inherited Hemoglobinopathies and Blood Disorders

## 1. Executive Overview

The therapeutic landscape for inherited blood disorders, historically defined by supportive care and the distinct limitations of allogeneic hematopoietic stem cell transplantation (HSCT), has been fundamentally reshaped by the advent of genomic medicine. The regulatory approval of exagamglogene autotemcel (exa-cel, marketed as Casgevy), the first CRISPR/Cas9-based therapy, marks a seminal inflection point in biotechnology, transitioning gene editing from a theoretical research capability to a validated clinical modality. This report provides an exhaustive, technical analysis of the current state of gene editing for hemoglobinopathies—specifically Sickle Cell Disease (SCD) and Transfusion-Dependent $\beta$-Thalassemia (TDT)—and extends its scope to emerging applications in Hemophilia and Fanconi Anemia.

While the clinical success of first-generation nuclease-based therapies has been transformative, offering functional cures to patients with severe disease, the field is rapidly pivoting toward next-generation technologies designed to address inherent limitations in safety, precision, and delivery. The current "state of the art" is defined by a triadic evolution: the shift from double-strand break (DSB) induction to precision "nickase" editing (base and prime editing) and retrotransposon-based "gene writing"; the transition from _ex vivo_ autologous processing to _in vivo_ delivery via targeted lipid nanoparticles (LNPs); and the replacement of genotoxic myeloablative conditioning with antibody-based, non-genotoxic regimens.

This report synthesizes data from pivotal Phase 3 clinical trials, nascent Phase 1/2 studies, and deep preclinical pipelines to offer a comprehensive assessment for researchers and investors. It critically evaluates the molecular mechanisms of action, the durability of clinical responses, the specific genotoxic risks associated with p53 activation and chromosomal translocations, and the health economic implications of high-cost one-time curative therapies in both developed and low-resource settings.

## 2. Molecular Pathophysiology and Therapeutic Targets

### 2.1 The Genetic Architecture of Hemoglobinopathies

The monogenic nature of SCD and TDT makes them archetypal candidates for gene correction. Both disorders stem from mutations in the _HBB_ gene on chromosome 11, which encodes the $\beta$-globin subunit of adult hemoglobin (HbA, $\alpha_2\beta_2$).

In Sickle Cell Disease, a specific missense mutation (A>T) in the sixth codon of the _HBB_ gene results in the substitution of the hydrophilic amino acid glutamic acid with the hydrophobic valine. This single amino acid change drastically alters the physiochemical properties of the resulting hemoglobin molecule (HbS). Under conditions of deoxygenation, the hydrophobic valine residue interacts with complementary hydrophobic sites on adjacent globin chains, triggering the polymerization of HbS molecules into rigid, long fibers.<sup>1</sup> These polymers distort the red blood cell (RBC) into the characteristic sickle shape, leading to membrane damage, hemolysis, and the occlusion of microvasculature, which manifests clinically as vaso-occlusive crises (VOCs) and progressive end-organ damage.<sup>1</sup>

In Transfusion-Dependent $\beta$-Thalassemia, a spectrum of over 200 mutations (including deletions, promoter mutations, and splicing defects) results in the reduction ($\beta^+$) or total absence ($\beta^0$) of $\beta$-globin synthesis. The pathophysiology is driven not only by the lack of hemoglobin but by the resultant imbalance in globin chains. Excess unbound $\alpha$-globin chains precipitate within erythroid precursors, causing oxidative damage and premature apoptosis in the bone marrow (ineffective erythropoiesis) as well as hemolysis of mature RBCs.<sup>1</sup>

### 2.2 The Fetal Hemoglobin Switching Paradigm

The most validated therapeutic strategy for both disorders is the reactivation of fetal hemoglobin (HbF, $\alpha_2\gamma_2$). During fetal development, $\gamma$-globin is the predominant $\beta$-like globin. Shortly after birth, a developmental switch occurs wherein $\gamma$-globin expression is silenced and $\beta$-globin expression is activated.

Clinical genetics provided the proof-of-concept for HbF reactivation as a therapeutic strategy. Individuals with Hereditary Persistence of Fetal Hemoglobin (HPFH) possess mutations that prevent this switch, maintaining high levels of HbF into adulthood. When HPFH is co-inherited with SCD or TDT mutations, the clinical phenotype is remarkably attenuated. In SCD, HbF exerts a potent anti-sickling effect because the $\gamma$-globin chains do not contain the valine residue and interfere with the polymerization of HbS. In TDT, $\gamma$-globin can pair with excess $\alpha$-chains to form functional HbF, ameliorating the chain imbalance and correcting anemia.<sup>2</sup>

### 2.3 BCL11A: The Master Transcriptional Repressor

The zinc-finger transcription factor BCL11A was identified via genome-wide association studies (GWAS) as a critical regulator of the hemoglobin switch. _BCL11A_ acts as a repressor of the $\gamma$-globin genes (_HBG1_ and _HBG2_). However, _BCL11A_ is widely expressed and essential for neurodevelopment and B-cell lymphopoiesis, making the disruption of the gene itself therapeutically inviable due to pleiotropic toxicity.

The breakthrough for safe therapeutic targeting came with the discovery of an erythroid-specific enhancer region located within intron 2 of the _BCL11A_ gene. This enhancer is required for _BCL11A_ expression specifically in the erythroid lineage but is dispensable in non-erythroid tissues. Disruption of this enhancer reduces BCL11A levels in erythroid cells, de-repressing $\gamma$-globin synthesis while preserving BCL11A function in other cell types.<sup>1</sup>

#### 2.3.1 Epigenetic Architecture: The Chromatin Rosette

Recent mechanistic elucidations have revealed that the regulation of _BCL11A_ is dependent on complex three-dimensional genome topology. High-resolution chromatin conformation capture studies indicate that the erythroid-specific enhancer folds into a "chromatin rosette" structure. This rosette facilitates the physical proximity of the enhancer to the _BCL11A_ promoter and other regulatory elements, stabilizing high-level transcription of the repressor.

Therapeutic editing at this locus operates on a structural level. The introduction of indels via CRISPR/Cas9 does not merely disrupt a linear binding sequence but physically destabilizes this chromatin rosette. The collapse of the 3D architecture prevents the enhancer from contacting the promoter, leading to transcriptional silencing of _BCL11A_ and the subsequent reactivation of HbF. St. Jude researchers have demonstrated that this structural disruption is the primary mechanism of action for current gene therapies, distinguishing them from strategies that might target the protein-coding sequence directly.<sup>6</sup>

## 3. First-Generation CRISPR Therapeutics: Exagamglogene Autotemcel

### 3.1 Mechanism of Action and Manufacturing

Exagamglogene autotemcel (exa-cel) utilizes the CRISPR/Cas9 system to target the erythroid-specific enhancer of _BCL11A_. The manufacturing process involves the collection of autologous CD34+ hematopoietic stem and progenitor cells (HSPCs) via apheresis after mobilization with plerixafor and/or granulocyte-colony stimulating factor (G-CSF). These cells are shipped to a manufacturing facility where they are electroporated with Cas9 ribonucleoprotein (RNP) complexes containing a single-guide RNA (sgRNA) specific to the enhancer sequence.<sup>1</sup>

The Cas9 nuclease induces a site-specific double-strand break (DSB). The cell's endogenous non-homologous end joining (NHEJ) machinery repairs the break, introducing random insertions or deletions (indels) that disrupt the enhancer functionality. This process is distinct from homology-directed repair (HDR) strategies that attempt to correct the gene sequence, as it relies on the error-prone nature of NHEJ which is active in all cell cycle phases, thereby achieving high editing efficiency in quiescent stem cells.<sup>2</sup>

### 3.2 Clinical Efficacy: The CLIMB Trials

The safety and efficacy of exa-cel have been evaluated in ongoing Phase 3 trials: CLIMB-111 (TDT) and CLIMB-121 (SCD), along with the long-term follow-up study CLIMB-131.

#### 3.2.1 CLIMB-121 (Severe Sickle Cell Disease)

Data from the CLIMB-121 trial demonstrate that exa-cel provides a highly durable functional cure for severe SCD.

- **Vaso-Occlusive Crisis (VOC) Elimination:** The primary endpoint was freedom from severe VOCs for at least 12 consecutive months (VF12). In the interim analysis, 29 of 30 evaluable patients (96.7%) achieved VF12 (95% CI: 83–100%; P<0.0001).
- **Hospitalization:** 30 of 30 evaluable patients (100%) remained free from inpatient hospitalizations related to VOCs for at least 12 consecutive months (HF12).
- **Durability:** Among 39 patients with sufficient follow-up, 36 remained VOC-free for durations ranging up to 41.4 months. The mean duration of VOC-free status in responders was 21.8 months.
- **Hematologic Recovery:** Following treatment, total hemoglobin levels normalized to a mean of >12 g/dL from Month 6 onward. Crucially, HbF comprised approximately 40% of total hemoglobin, with a pancellular distribution (detectable in ≥95% of RBCs), which effectively prevents sickling.<sup>4</sup>

#### 3.2.2 CLIMB-111 (Transfusion-Dependent Thalassemia)

In TDT patients, the goal is transfusion independence (TI).

- **Transfusion Independence:** 24 of 27 evaluable patients (88.9%) achieved the primary endpoint of transfusion independence for at least 12 consecutive months (TI12) with a mean weighted hemoglobin of at least 9 g/dL.
- **Burden Reduction:** Of the three patients who did not achieve TI12, two achieved substantial reductions in transfusion volume (80% and 96%), and one subsequently achieved transfusion freedom.
- **Iron Homeostasis:** The cessation of transfusions allows for the gradual normalization of iron stores, reducing the need for chelation therapy.<sup>10</sup>

### 3.3 Safety Profile and Limitations

The safety profile of exa-cel largely reflects the risks associated with myeloablative conditioning and autologous transplantation.

- **Adverse Events (AEs):** The most frequent AEs included nausea (66.7%), stomatitis (61.9%), febrile neutropenia (52.4%), and thrombocytopenia, all consistent with busulfan conditioning.
- **Serious Adverse Events (SAEs):** While no SAEs were attributed to the exa-cel drug product itself in the interim analysis, serious complications such as veno-occlusive disease (VOD) are known risks of busulfan. One death occurred due to respiratory failure from COVID-19, which was deemed unrelated to the therapy.<sup>4</sup>
- **Fertility and Long-Term Risks:** Myeloablative busulfan is gonadotoxic, carrying a high risk of permanent infertility. Furthermore, alkylating agents increase the lifetime risk of secondary malignancies. While exa-cel does not carry the "boxed warning" for hematologic malignancy seen with the lentiviral gene therapy Lyfgenia (due to insertional oncogenesis risks), the potential for off-target editing or complex chromosomal rearrangements remains a theoretical long-term concern.<sup>12</sup>

## 4. Mechanisms of Genotoxicity in Nuclease-Based Editing

The primary molecular liability of first-generation CRISPR therapies is their reliance on the induction of Double-Strand Breaks (DSBs). The cellular response to DSBs triggers distinct pathways that pose genotoxic risks to HSCs.

### 4.1 The p53-Mediated DNA Damage Response

Hematopoietic stem cells possess a highly sensitive DNA Damage Response (DDR) mechanism governed by the _TP53_ gene. The induction of a DSB by Cas9 is perceived by the cell as a critical genotoxic event.

- **Cell Cycle Arrest and Apoptosis:** Activation of p53 leads to the upregulation of _CDKN1A_ (p21), causing cell cycle arrest or apoptosis. This response explains the often significant drop in cell viability and yield observed during the _ex vivo_ manufacturing process.<sup>14</sup>
- **Selection Pressure for Oncogenic Clones:** A profound safety concern is the potential for "selection pressure." Since p53-competent cells are more likely to arrest or die following editing, the process may inadvertently enrich for pre-existing HSC clones that harbor p53 mutations or other DDR defects. If such clones are expanded and infused, they could predispose the patient to donor-derived leukemia or myelodysplastic syndrome (MDS). Studies have confirmed that Cas9-induced DSBs upregulate the p53 pathway specifically in wild-type cells, providing a competitive advantage to p53-mutant cells.<sup>15</sup>

### 4.2 Chromosomal Translocations

When multiple DSBs are induced simultaneously within a cell, the NHEJ machinery may erroneously ligate disparate chromosomal ends, resulting in translocations.

- **Multiplex Editing Risks:** Strategies that attempt to edit multiple loci simultaneously (e.g., disrupting _BCL11A_ and the _HBG_ promoter to maximize HbF) have been shown to generate chromosomal translocations at frequencies of approximately 1.0% in preclinical models. Even strategies using sequential editing (editing one locus, then the other) cannot completely eliminate this risk.<sup>17</sup>
- **On-Target Rearrangements:** Even at a single locus, the repair of a DSB can result in large deletions (spanning kilobases) or complex rearrangements that may affect neighboring genes. In the context of _BCL11A_, large deletions could theoretically affect the function of the _BCL11A_ gene in other lineages if the deletion extends beyond the erythroid enhancer.<sup>18</sup>

## 5. Next-Generation Precision Editing: Base and Prime Editing

To mitigate the risks inherent to DSBs, the field is advancing "nickase-based" technologies that modify the genome without severing the DNA double helix.

### 5.1 Base Editing: Chemical Conversion

Base editors (BEs) consist of a Cas9 nickase (nCas9) fused to a deaminase enzyme. The nCas9 localizes to the target site and nicks the non-edited strand, while the deaminase chemically converts a specific nucleotide base on the other strand.

- **Mechanism:** Adenine Base Editors (ABEs) deaminate adenosine to inosine, which is read as guanosine by polymerase, effectively converting an A•T base pair to a G•C base pair. Cytosine Base Editors (CBEs) convert C•G to T•A.
- **Therapeutic Application:** In the context of hemoglobinopathies, ABEs are being used to disrupt the _BCL11A_ enhancer or to introduce mutations in the _HBG_ promoter that mimic HPFH (e.g., the -175 A>G mutation). Preclinical data from St. Jude Children's Research Hospital indicates that ABE-mediated installation of the -175 mutation is highly potent, inducing uniform HbF expression.<sup>5</sup>
- **Beam Therapeutics (BEAM-101):** The lead clinical candidate, BEAM-101, uses an ABE to introduce missense mutations in the _HBG1/2_ promoters to reactivate HbF. Phase 1/2 trials are currently enrolling, with initial data expected to demonstrate whether this approach offers a superior safety profile regarding translocations compared to Casgevy.<sup>19</sup>
- **Limitations:** The classic SCD mutation is an A>T transversion. Standard base editors are limited to transition mutations (purine to purine, pyrimidine to pyrimidine) and cannot directly revert the T back to A. Thus, base editing in SCD is largely restricted to HbF induction strategies rather than direct repair of the pathogenic allele.<sup>21</sup>

### 5.2 Prime Editing: Search-and-Replace

Prime editing represents a quantum leap in editing versatility, capable of installing any base substitution, small insertion, or deletion without DSBs or donor DNA.

- **Mechanism:** The prime editor is a fusion of nCas9 and an engineered reverse transcriptase (RT). It utilizes a prime editing guide RNA (pegRNA) that contains both the target recognition sequence and a reverse transcription template encoding the desired edit. Upon nicking the target strand, the RT uses the pegRNA template to synthesize the corrected DNA sequence directly onto the genomic strand.<sup>21</sup>
- **SCD Correction:** Prime editing can perform the specific T-to-A conversion required to revert the HbS allele (Glu6Val) to the wild-type HbA sequence. This offers the potential for a true physiological cure, restoring wild-type hemoglobin rather than relying on compensatory HbF.
- **Preclinical Efficacy:** Collaborative studies by the Broad Institute and St. Jude have demonstrated prime editing efficiency of up to 41% in SCD patient-derived HSCs. In mouse xenograft models, these cells maintained long-term engraftment (17 weeks), with 45% of circulating RBCs expressing wild-type hemoglobin—significantly exceeding the estimated 20% threshold required for therapeutic benefit. Crucially, prime editing showed dramatically reduced off-target editing and negligible p53 activation compared to Cas9 nuclease strategies.<sup>21</sup>

## 6. Fourth-Generation Innovation: Gene Writing & Retrotransposons

While base and prime editing offer precision for small changes, the insertion of large genetic payloads (e.g., whole genes or exons) usually requires viral vectors or inefficient HDR. "Gene Writing," pioneered by Tessera Therapeutics, leverages the evolutionary biology of mobile genetic elements (MGEs) to address this gap.

### 6.1 Target-Primed Reverse Transcription (TPRT)

Tessera's RNA Gene Writers are engineered from non-LTR retrotransposons. These naturally occurring elements mobilize within genomes via an RNA intermediate using a mechanism called Target-Primed Reverse Transcription (TPRT).

- **Mechanism:** The Gene Writer system is delivered as an all-RNA composition (mRNA encoding the Writer protein + a template RNA). The Writer protein binds the template RNA, recognizes the specific genomic target site, and nicks one strand of the DNA. It then uses the 3'-hydroxyl group of the nicked DNA as a primer to reverse transcribe the RNA template directly into the genome.<sup>24</sup>
- **Advantages:** This mechanism avoids DSBs entirely and does not rely on host repair pathways (like HDR) that are downregulated in quiescent stem cells. This allows for the efficient insertion of large sequences (e.g., replacing a defective exon or inserting a therapeutic transgene) in non-dividing cells.<sup>25</sup>

### 6.2 Preclinical Validation

Data presented at the American Society of Hematology (ASH) meeting demonstrated the potency of this platform in non-human primates (NHPs).

- **Efficiency:** RNA Gene Writers achieved approximately 40% editing of the _HBB_ gene in long-term HSCs after a single dose, and up to 60% after two doses. This level of correction in long-term repopulating cells is unprecedented for a non-viral, large-insertion technology.<sup>24</sup>
- **Delivery:** Because the components are RNA-based, they are compatible with Lipid Nanoparticle (LNP) delivery, positioning Gene Writing as a prime candidate for _in vivo_ therapy.<sup>25</sup>

## 7. The Delivery Frontier: Transitioning to In Vivo Therapy

The current standard of care involves _ex vivo_ gene editing: a complex, multi-step process involving mobilization, apheresis, _ex vivo_ manufacturing, cryopreservation, and re-infusion. This infrastructure-heavy model limits patient access and scalability. The "Holy Grail" of gene therapy is a single-administration, _in vivo_ treatment that targets HSCs directly in the bone marrow.

### 7.1 Lipid Nanoparticles (LNPs) and Tropism

Standard LNPs, such as those used in mRNA vaccines, naturally accumulate in the liver due to ApoE-mediated uptake by hepatocytes via the LDL receptor. While effective for liver-directed therapies (e.g., transthyretin amyloidosis or Hemophilia gene insertion), this "liver sink" phenomenon prevents effective delivery to the bone marrow.<sup>28</sup>

### 7.2 Antibody-Targeted LNPs (t-LNPs)

To overcome liver tropism and target HSCs, researchers are developing targeted LNPs (t-LNPs) conjugated with monoclonal antibodies specific to HSC surface markers.

- **CD117 (c-Kit) Targeting:** CD117 is a receptor tyrosine kinase expressed on HSPCs. Conjugation of anti-CD117 antibodies (e.g., clone 2B8) to LNPs via maleimide-thiol chemistry facilitates receptor-mediated endocytosis. CD117 is particularly suitable because it internalizes rapidly upon ligand binding. Preclinical studies have shown that a single intravenous injection of CD117-t-LNPs can deliver Cre recombinase or Cas9 mRNA to bone marrow HSCs, achieving ~90% editing in reporter mouse models without requiring cell harvest.<sup>30</sup>
- **CD45 Targeting:** CD45 is a pan-leukocyte marker expressed on all nucleated blood cells. Studies utilizing anti-CD45 LNPs have demonstrated the ability to edit HSCs _in vivo_ in both adult mice and _in utero_ fetal models. This approach could potentially allow for the correction of genetic defects before birth, preventing irreversible organ damage.<sup>32</sup>
- **Clinical Implications:** Successful development of t-LNPs would transform gene therapy from a transplant procedure to a pharmaceutical infusion, drastically reducing cost and increasing accessibility in low-resource settings.

## 8. Revolutionizing Conditioning: Non-Genotoxic Regimens

Even with _ex vivo_ editing, the requirement for toxic conditioning with alkylating agents (busulfan) to "clear niche space" remains a major safety and acceptability barrier. Busulfan causes mucositis, alopecia, permanent infertility, and secondary malignancies.

### 8.1 Antibody-Drug Conjugates (ADCs)

To replace chemotherapy, the field is developing antibody-based conditioning (ABC) that selectively depletes HSCs.

- **Briquilimab (JSP191):** Developed by Jasper Therapeutics, briquilimab is a monoclonal antibody targeting CD117 (c-Kit). It blocks the binding of Stem Cell Factor (SCF), depriving HSCs of critical survival signals and leading to their apoptosis.
  - **Clinical Data:** In a Phase 1/2 trial for SCD, briquilimab combined with low-dose irradiation resulted in successful engraftment in all treated patients. Participants achieved 100% donor myeloid chimerism rapidly (within 30-100 days) with no severe adverse events related to the antibody, contrasting sharply with the toxicity of busulfan.<sup>34</sup>
  - **Mechanism:** By acting as an antagonist rather than a cytotoxic delivery vehicle, briquilimab offers a wide therapeutic window.
- **Cytotoxic ADCs (MGTA-117):** Magenta Therapeutics developed MGTA-117, an anti-CD117 antibody conjugated to the toxin amanitin. While highly potent in preclinical models, the clinical trial in AML/MDS was halted after a Grade 5 (fatal) serious adverse event involving respiratory failure and cardiac arrest. This highlights the risks associated with systemic administration of potent toxins, even when targeted, and suggests that non-toxin-based depletion (like briquilimab) or rapidly cleared ADCs may be safer pathways.<sup>37</sup>

## 9. Expanding Indications: Hemophilia and Fanconi Anemia

### 9.1 Hemophilia A and B

For Hemophilia, the goal is gene _addition_ rather than correction. The size of the Factor VIII gene (_F8_) presents a challenge for AAV vectors, which have limited cargo capacity.

- **In Vivo Gene Insertion:** Intellia and Regeneron are advancing CRISPR/Cas9-based _in vivo_ gene insertion. Their strategy targets the albumin (_ALB_) locus in the liver. By inserting the Factor IX (_F9_) or Factor VIII (_F8_) gene into this highly expressed locus, the liver becomes a factory for clotting factors.
- **Advantages:** Unlike AAV-based gene therapy (e.g., Roctavian), which exists as an episome and dilutes over time as hepatocytes divide (limiting durability in pediatric patients), genome insertion is permanent and passed to daughter cells. This offers the potential for a lifelong cure with a single dose.<sup>40</sup>

### 9.2 Fanconi Anemia (FA)

FA represents the ultimate challenge for gene editing due to the inherent DNA repair defects in patient cells.

- **Challenges:** FA cells are hypersensitive to DSBs and conditioning agents. _Ex vivo_ culture often leads to HSC exhaustion.
- **Lentiviral Success:** Clinical trials using lentiviral vectors (RP-L102) without conditioning have shown that gene-corrected FA HSCs have a natural survival advantage. Over months to years, these corrected cells progressively repopulate the bone marrow, reversing bone marrow failure.<sup>43</sup>
- **Editing Potential:** To avoid the risks of insertional mutagenesis with lentiviruses, research is exploring _in vivo_ delivery of mRNA via LNPs to transiently express FANC proteins or using base/prime editing which avoids the lethal DSBs that FA cells cannot repair.<sup>45</sup>

## 10. Global Health and Health Economics

### 10.1 The Access Gap and Global Burden

The majority of the world's SCD burden resides in sub-Saharan Africa and India. The current cost of Casgevy ($2.2 million) and Lyfgenia ($3.1 million), combined with the requirement for sophisticated apheresis and transplant units, creates a "genetic divide" where cures are available only to a fraction of the global patient population.<sup>47</sup>

### 10.2 The "Global Gene Therapy Initiative"

To address this, the Bill & Melinda Gates Foundation and the NIH have launched a collaborative initiative with a target to develop affordable, scalable, _in vivo_ gene therapies for SCD and HIV.

- **Target Product Profile:** A "single-shot" cure administrable in outpatient settings with minimal conditioning.
- **Investment:** Over $200 million has been committed to developing non-viral delivery vectors (like the t-LNPs discussed above) and building clinical trial capacity in Africa.<sup>49</sup>
- **Capacity Building:** Trials are slowly expanding to sites in Ghana, Tanzania, and Nigeria. A landmark study by Fifty1 AI Labs, funded by the Gates Foundation, recently completed a comprehensive mapping of real-world SCD data in Africa to facilitate future trial designs and drug repurposing.<sup>52</sup>

### 10.3 Reimbursement Innovation

In the US, the high upfront cost has driven the adoption of Outcomes-Based Agreements (OBAs). The Centers for Medicare & Medicaid Services (CMS) launched the Cell and Gene Therapy Access Model in 2025. Under this model, state Medicaid agencies can sign agreements where manufacturers (Vertex, bluebird bio) must provide rebates if the therapy fails to achieve specific clinical outcomes (e.g., recurrence of VOCs or hospitalization).<sup>12</sup> This risk-sharing model is essential to mitigate the financial uncertainty of these novel therapies for payers.

## 11. Commercial Landscape and Future Outlook

The sector is characterized by intense competition between editing modalities.

- **Vertex (Casgevy):** First-mover advantage, established commercial infrastructure, but relies on first-gen Cas9/NHEJ technology.
- **Bluebird Bio (Lyfgenia):** Offers a lentiviral alternative but burdened by the "black box" safety warning and manufacturing complexity.
- **Beam Therapeutics:** Advancing base editing (BEAM-101) with a potentially safer profile. Their "Wave 3" strategy focuses explicitly on _in vivo_ delivery.<sup>20</sup>
- **Intellia/Regeneron:** Leading the _in vivo_ race with systemic LNP platforms validated in ATTR and HAE, now pivoting to Hemophilia.<sup>54</sup>
- **Tessera Therapeutics:** The "dark horse" with Gene Writing technology that could disrupt the field by enabling large-cargo insertions without viral vectors.<sup>27</sup>

## 12. Conclusion

The approval of Casgevy is a historic validation of CRISPR as a medicine, but it represents the "Model T" of gene editing: functional and revolutionary, yet complex and rudimentary compared to what follows. The field is aggressively moving away from the "cut-and-disrupt" paradigm of nucleases toward the "search-and-replace" precision of prime editing and gene writing. Concurrently, the operational model is shifting from high-burden _ex vivo_ transplantation to scalable _in vivo_ pharmaceutical delivery.

The convergence of non-genotoxic conditioning (briquilimab), target-specific delivery (t-LNPs), and high-fidelity editing (Gene Writers) holds the promise of transforming hemoglobinopathy treatment from a rare, high-risk procedure into a broadly accessible standard of care. For investors and researchers, the value proposition lies not just in the current approvals, but in these platform technologies that will democratize genomic medicine for the global patient population.

**Table 1: Comparison of Gene Editing Modalities for Hemoglobinopathies**

| **Feature**            | **Cas9 Nuclease (Casgevy)** | **Base Editing (BEAM-101)**      | **Prime Editing (Preclinical)**  | **Gene Writing (Tessera)**       |
| ---------------------- | --------------------------- | -------------------------------- | -------------------------------- | -------------------------------- |
| **DNA Modification**   | Double-Strand Break (DSB)   | Single-Strand Nick + Deamination | Single-Strand Nick + RT Template | Single-Strand Nick + TPRT        |
| **Mechanism**          | NHEJ (Disruption)           | Chemical Conversion (A>G, C>T)   | Reverse Transcription (Any Base) | Retrotransposon-based Insertion  |
| **SCD Strategy**       | Induce HbF (_BCL11A_ KO)    | Induce HbF or benign variants    | True Correction (HbS to HbA)     | True Correction or Gene Addition |
| **Genotoxicity Risk**  | High (Translocations, p53)  | Low (No DSBs)                    | Low (No DSBs)                    | Low (No DSBs)                    |
| **Delivery Vehicle**   | Electroporation (RNP)       | Electroporation / LNP            | Electroporation / LNP            | LNP (All-RNA)                    |
| **Development Status** | Approved (FDA/EMA)          | Phase 1/2 Clinical Trials        | Preclinical / Lead Optimization  | Preclinical (NHP POC)            |

## References

1.  How Does CASGEVY® Work? | CASGEVY® (exagamglogene autotemcel) MOA, accessed December 16, 2025, [https://www.casgevyhcp.com/mechanism-of-action](https://www.casgevyhcp.com/mechanism-of-action)
2.  What is the mechanism of Exagamglogene Autotemcel? - Patsnap Synapse, accessed December 16, 2025, [https://synapse.patsnap.com/article/what-is-the-mechanism-of-exagamglogene-autotemcel](https://synapse.patsnap.com/article/what-is-the-mechanism-of-exagamglogene-autotemcel)
3.  New Treatment Options for Sickle Cell Disease | Health Action Council, accessed December 16, 2025, [https://healthactioncouncil.org/resources/blog/new-treatment-options-for-sickle-cell-disease/](https://healthactioncouncil.org/resources/blog/new-treatment-options-for-sickle-cell-disease/)
4.  Exagamglogene Autotemcel for Severe Sickle Cell Disease ..., accessed December 16, 2025, [https://www.researchgate.net/publication/376149201_Exagamglogene_Autotemcel_for_Severe_Sickle_Cell_Disease](https://www.researchgate.net/publication/376149201_Exagamglogene_Autotemcel_for_Severe_Sickle_Cell_Disease)
5.  Next-generation gene editing for sickle cell disease | St. Jude ..., accessed December 16, 2025, [https://www.stjude.org/research/why-st-jude/scientific-report/2024/next-generation-gene-editing-for-sickle-cell-disease.html](https://www.stjude.org/research/why-st-jude/scientific-report/2024/next-generation-gene-editing-for-sickle-cell-disease.html)
6.  Gene therapy for sickle cell and β-thalassemia works by disrupting three-dimensional genome structure - St. Jude Children's Research Hospital, accessed December 16, 2025, [https://www.stjude.org/media-resources/news-releases/2025-medicine-science-news/gene-therapy-for-sickle-cell-and-beta-thalassemia-works-by-disrupting-three-dimensional-genome-structure.html](https://www.stjude.org/media-resources/news-releases/2025-medicine-science-news/gene-therapy-for-sickle-cell-and-beta-thalassemia-works-by-disrupting-three-dimensional-genome-structure.html)
7.  New method reactivates fetal hemoglobin without gene editing | Sickle Cell Disease News, accessed December 16, 2025, [https://sicklecellanemianews.com/news/new-method-reactivates-fetal-hemoglobin-without-gene-editing/](https://sicklecellanemianews.com/news/new-method-reactivates-fetal-hemoglobin-without-gene-editing/)
8.  Exagamglogene Autotemcel for Severe Sickle Cell Disease - PubMed, accessed December 16, 2025, [https://pubmed.ncbi.nlm.nih.gov/38661449/](https://pubmed.ncbi.nlm.nih.gov/38661449/)
9.  Durable Clinical Benefits with Exagamglogene Autotemcel for Severe Sickle Cell Disease, accessed December 16, 2025, [https://ash.confex.com/ash/2024/webprogram/Paper204001.html](https://ash.confex.com/ash/2024/webprogram/Paper204001.html)
10. Positive Results From Pivotal Trials of exa-cel for Transfusion-Dependent Beta Thalassemia and Severe Sickle Cell Disease Presented at the 2023 Annual European Hematology Association (EHA) Congress - CRISPR Therapeutics, accessed December 16, 2025, [https://crisprtx.com/about-us/press-releases-and-presentations/positive-results-from-pivotal-trials-of-exa-cel-for-transfusion-dependent-beta-thalassemia-and-severe-sickle-cell-disease-presented-at-the-2023-annual-european-hematology-association-eha-congress](https://crisprtx.com/about-us/press-releases-and-presentations/positive-results-from-pivotal-trials-of-exa-cel-for-transfusion-dependent-beta-thalassemia-and-severe-sickle-cell-disease-presented-at-the-2023-annual-european-hematology-association-eha-congress)
11. CLIMB-111 and CLIMB-121 phase III trials of Exa-Cel meet their primary endpoint in beta thalassemia or severe sickle cell disease.- Vertex Pharma - Medthority, accessed December 16, 2025, [https://www.medthority.com/news/2023/6/climb-111-and-climb-121-phase-iii-trials-of-exa-cel-meet-their-primary-endpoint-in-beta-thalassemia-or-severe-sickle-cell-disease.--vertex-pharma](https://www.medthority.com/news/2023/6/climb-111-and-climb-121-phase-iii-trials-of-exa-cel-meet-their-primary-endpoint-in-beta-thalassemia-or-severe-sickle-cell-disease.--vertex-pharma)
12. bluebird bio Announces First Outcomes-Based Agreement with Medicaid for Sickle Cell Disease Gene Therapy, accessed December 16, 2025, [https://investor.bluebirdbio.com/news-releases/news-release-details/bluebird-bio-announces-first-outcomes-based-agreement-medicaid](https://investor.bluebirdbio.com/news-releases/news-release-details/bluebird-bio-announces-first-outcomes-based-agreement-medicaid)
13. Biden-Harris Administration Takes Next Steps to Increase Access to Sickle Cell Disease Treatments | CMS, accessed December 16, 2025, [https://www.cms.gov/newsroom/press-releases/biden-harris-administration-takes-next-steps-increase-access-sickle-cell-disease-treatments](https://www.cms.gov/newsroom/press-releases/biden-harris-administration-takes-next-steps-increase-access-sickle-cell-disease-treatments)
14. The p53 challenge of hematopoietic stem cell gene editing - PMC - NIH, accessed December 16, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10331021/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10331021/)
15. Cas9 activates the p53 pathway and selects for p53-inactivating mutations - PMC - NIH, accessed December 16, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7343612/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7343612/)
16. P53 toxicity is a hurdle to CRISPR/CAS9 screening and engineering in human pluripotent stem cells - ResearchGate, accessed December 16, 2025, [https://www.researchgate.net/publication/346925624_P53_toxicity_is_a_hurdle_to_CRISPRCAS9_screening_and_engineering_in_human_pluripotent_stem_cells](https://www.researchgate.net/publication/346925624_P53_toxicity_is_a_hurdle_to_CRISPRCAS9_screening_and_engineering_in_human_pluripotent_stem_cells)
17. Paper: Multiplex CRISPR/Cas9 Genome Editing Targeting the BCL11A/HBG Axis Maximizes Fetal Hemoglobin Reinduction but Generates Chromosomal Translocations Which Persist In Vivo - Abstract, accessed December 16, 2025, [https://ash.confex.com/ash/2020/webprogram/Paper138539.html](https://ash.confex.com/ash/2020/webprogram/Paper138539.html)
18. Safety and efficacy study of CRISPR/Cas9 treatment of sickle cell disease in clinically relevant conditions highlights disease-specific responses | bioRxiv, accessed December 16, 2025, [https://www.biorxiv.org/content/10.1101/2024.01.14.575586v1.full-text](https://www.biorxiv.org/content/10.1101/2024.01.14.575586v1.full-text)
19. Beam Therapeutics Highlights Progress Across Base Editing Portfolio and Outlines 2024 Anticipated Milestones, accessed December 16, 2025, [https://investors.beamtx.com/news-releases/news-release-details/beam-therapeutics-highlights-progress-across-base-editing/](https://investors.beamtx.com/news-releases/news-release-details/beam-therapeutics-highlights-progress-across-base-editing/)
20. Beam Therapeutics Announces Progress in Hematology and Genetic Disease Franchises and Outlines Key 2025 Anticipated Catalysts, accessed December 16, 2025, [https://investors.beamtx.com/news-releases/news-release-details/beam-therapeutics-announces-progress-hematology-and-genetic/](https://investors.beamtx.com/news-releases/news-release-details/beam-therapeutics-announces-progress-hematology-and-genetic/)
21. Prime editing shows proof of concept for treating sickle cell disease - Broad Institute, accessed December 16, 2025, [https://www.broadinstitute.org/news/prime-editing-shows-proof-concept-treating-sickle-cell-disease](https://www.broadinstitute.org/news/prime-editing-shows-proof-concept-treating-sickle-cell-disease)
22. Efficient and error-free correction of sickle mutation in human erythroid cells using prime editor-2 - Frontiers, accessed December 16, 2025, [https://www.frontiersin.org/journals/genome-editing/articles/10.3389/fgeed.2022.1085111/full](https://www.frontiersin.org/journals/genome-editing/articles/10.3389/fgeed.2022.1085111/full)
23. Prime editing successfully corrects sickle cell mutation - Front Line Genomics, accessed December 16, 2025, [https://frontlinegenomics.com/prime-editing-successfully-corrects-sickle-cell-mutation/](https://frontlinegenomics.com/prime-editing-successfully-corrects-sickle-cell-mutation/)
24. Tessera Therapeutics Showcases New ... - Tessera Therapeutics, accessed December 16, 2025, [https://www.tesseratherapeutics.com/news/tessera-therapeutics-showcases-new-preclinical-data-demonstrating-progress-of-in-vivo-programs-for-sickle-cell-disease-and-t-cell-therapies-at-the-67th-american-society-of-hematology-annual-meeting](https://www.tesseratherapeutics.com/news/tessera-therapeutics-showcases-new-preclinical-data-demonstrating-progress-of-in-vivo-programs-for-sickle-cell-disease-and-t-cell-therapies-at-the-67th-american-society-of-hematology-annual-meeting)
25. Michael C. Holmes's research while affiliated with Tessera Technologies and other places, accessed December 16, 2025, [https://www.researchgate.net/scientific-contributions/Michael-C-Holmes-2267623610](https://www.researchgate.net/scientific-contributions/Michael-C-Holmes-2267623610)
26. Cecilia Cotta-Ramusino's research works | Tessera Technologies and other places, accessed December 16, 2025, [https://www.researchgate.net/scientific-contributions/Cecilia-Cotta-Ramusino-2119401841](https://www.researchgate.net/scientific-contributions/Cecilia-Cotta-Ramusino-2119401841)
27. Tessera Therapeutics Showcases New Preclinical Data Demonstrating Progress of In Vivo Programs for Sickle Cell Disease and T Cell Therapies at the 67th American Society of Hematology Annual Meeting - GlobeNewswire, accessed December 16, 2025, [https://www.globenewswire.com/news-release/2025/12/08/3201455/0/en/Tessera-Therapeutics-Showcases-New-Preclinical-Data-Demonstrating-Progress-of-In-Vivo-Programs-for-Sickle-Cell-Disease-and-T-Cell-Therapies-at-the-67th-American-Society-of-Hematolo.html](https://www.globenewswire.com/news-release/2025/12/08/3201455/0/en/Tessera-Therapeutics-Showcases-New-Preclinical-Data-Demonstrating-Progress-of-In-Vivo-Programs-for-Sickle-Cell-Disease-and-T-Cell-Therapies-at-the-67th-American-Society-of-Hematolo.html)
28. Therapeutic in vivo delivery of gene editing agents - PMC - PubMed Central, accessed December 16, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9454337/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9454337/)
29. Advances in Antibody-Targeted Lipid Nanoparticles (Ab-LNPs) and Their Emerging Therapeutic Applications | Biopharma PEG, accessed December 16, 2025, [https://www.biochempeg.com/article/449.html](https://www.biochempeg.com/article/449.html)
30. In Vivo RNA Delivery to Hematopoietic Stem and Progenitor Cells ..., accessed December 16, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10103292/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10103292/)
31. In Vivo RNA Delivery to Hematopoietic Stem and Progenitor Cells via Targeted Lipid Nanoparticles | Nano Letters - ACS Publications, accessed December 16, 2025, [https://pubs.acs.org/doi/10.1021/acs.nanolett.3c00304](https://pubs.acs.org/doi/10.1021/acs.nanolett.3c00304)
32. In Vivo RNA delivery by targeted lipid nanoparticles enable gene editing in hematopoietic stem cells and T cells - ResearchGate, accessed December 16, 2025, [https://www.researchgate.net/publication/398356226_In_Vivo_RNA_delivery_by_targeted_lipid_nanoparticles_enable_gene_editing_in_hematopoietic_stem_cells_and_T_cells](https://www.researchgate.net/publication/398356226_In_Vivo_RNA_delivery_by_targeted_lipid_nanoparticles_enable_gene_editing_in_hematopoietic_stem_cells_and_T_cells)
33. In utero delivery of targeted ionizable lipid nanoparticles facilitates in vivo gene editing of hematopoietic stem cells | PNAS, accessed December 16, 2025, [https://www.pnas.org/doi/10.1073/pnas.2400783121](https://www.pnas.org/doi/10.1073/pnas.2400783121)
34. Jasper Therapeutics Announces Positive Clinical Data from a Phase I/II Trial of Briquilimab as a Conditioning Treatment in Sickle Cell Disease and Beta Thalassemia, accessed December 16, 2025, [https://ir.jaspertherapeutics.com/news-releases/news-release-details/jasper-therapeutics-announces-positive-clinical-data-phase-iii/](https://ir.jaspertherapeutics.com/news-releases/news-release-details/jasper-therapeutics-announces-positive-clinical-data-phase-iii/)
35. Jasper Therapeutics Announces Positive Follow-up Clinical Data from Investigator-Sponsored Study of Briquilimab Conditioning in Sickle Cell Disease Patients - FirstWord Pharma, accessed December 16, 2025, [https://firstwordpharma.com/story/5707320](https://firstwordpharma.com/story/5707320)
36. Jasper Therapeutics Reports Clinical Data Update from Briquilimab Studies in Chronic Spontaneous Urticaria, accessed December 16, 2025, [https://ir.jaspertx.com/news-releases/news-release-details/jasper-therapeutics-reports-clinical-data-update-briquilimab/](https://ir.jaspertx.com/news-releases/news-release-details/jasper-therapeutics-reports-clinical-data-update-briquilimab/)
37. MGTA-117 Trial in R/R AML and MDS Stops Due to Safety Concerns | Targeted Oncology, accessed December 16, 2025, [https://www.targetedonc.com/view/mgta-117-trial-in-r-r-aml-and-mds-stops-due-to-safety-concerns](https://www.targetedonc.com/view/mgta-117-trial-in-r-r-aml-and-mds-stops-due-to-safety-concerns)
38. Phase 1/2 Trial Pauses Enrollment for Evaluation of MGTA-117 in AML/MDS After Patient Death | OncLive, accessed December 16, 2025, [https://www.onclive.com/view/phase-1-2-trial-pauses-enrollment-for-evaluation-of-mgta-117-in-aml-mds-after-patient-death](https://www.onclive.com/view/phase-1-2-trial-pauses-enrollment-for-evaluation-of-mgta-117-in-aml-mds-after-patient-death)
39. Magenta halts high-dose group in leukemia trial after serious adverse events, accessed December 16, 2025, [https://www.fiercebiotech.com/biotech/magenta-halts-high-dose-group-leukemia-trial-after-serious-adverse-events](https://www.fiercebiotech.com/biotech/magenta-halts-high-dose-group-leukemia-trial-after-serious-adverse-events)
40. SEC Filing - Intellia Therapeutics - investor relations, accessed December 16, 2025, [https://ir.intelliatx.com/node/9891/html](https://ir.intelliatx.com/node/9891/html)
41. Regeneron and Intellia Therapeutics Expand Collaboration to Develop CRISPR/Cas9-Based Treatments, accessed December 16, 2025, [https://investor.regeneron.com/news-releases/news-release-details/regeneron-and-intellia-therapeutics-expand-collaboration-develop/](https://investor.regeneron.com/news-releases/news-release-details/regeneron-and-intellia-therapeutics-expand-collaboration-develop/)
42. How Close Are We to Achieving Durable and Efficacious Gene Therapy for Hemophilia A and B? - NIH, accessed December 16, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12563086/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12563086/)
43. Long-term success of gene therapy in patients with Fanconi anemia, accessed December 16, 2025, [https://www.genethon.com/long-term-success-of-gene-therapy-in-patients-with-fanconi-anemia/](https://www.genethon.com/long-term-success-of-gene-therapy-in-patients-with-fanconi-anemia/)
44. Phase I/II Gene Therapy Trial of Fanconi anemia patients with a new Orphan Drug consisting of a lentiviral vector carrying the FANCA gene: A Coordinated International Action - CORDIS, accessed December 16, 2025, [https://cordis.europa.eu/project/id/305421/reporting](https://cordis.europa.eu/project/id/305421/reporting)
45. Children's Hospital of Philadelphia Preclinical Study Unveils Promising New Treatment Approach for Fanconi Anemia Patients, accessed December 16, 2025, [https://www.chop.edu/news/childrens-hospital-philadelphia-preclinical-study-unveils-promising-new-treatment-approach](https://www.chop.edu/news/childrens-hospital-philadelphia-preclinical-study-unveils-promising-new-treatment-approach)
46. In Vivo Correction of a Genetically Humanized Fanconi Anemia Mouse Bone Marrow Failure Model Using Digital Editing Technologies | Blood - ASH Publications, accessed December 16, 2025, [https://ashpublications.org/blood/article/144/Supplement%201/7461/526396/In-Vivo-Correction-of-a-Genetically-Humanized](https://ashpublications.org/blood/article/144/Supplement%201/7461/526396/In-Vivo-Correction-of-a-Genetically-Humanized)
47. SCDAA Statement About Gene Therapy Approval - Sickle Cell Disease Association of America Inc., accessed December 16, 2025, [https://www.sicklecelldisease.org/2023/12/08/scdaa-statement-about-gene-therapy-approval/](https://www.sicklecelldisease.org/2023/12/08/scdaa-statement-about-gene-therapy-approval/)
48. Pricey new gene therapies for sickle cell pose access test | BioPharma Dive, accessed December 16, 2025, [https://www.biopharmadive.com/news/crispr-sickle-cell-price-millions-gene-therapy-vertex-bluebird/702066/](https://www.biopharmadive.com/news/crispr-sickle-cell-price-millions-gene-therapy-vertex-bluebird/702066/)
49. NIH launches new collaboration to develop gene-based cures for sickle cell disease and HIV on global scale, accessed December 16, 2025, [https://www.nhlbi.nih.gov/news/2019/nih-launches-new-collaboration-develop-gene-based-cures-sickle-cell-disease-and-hiv](https://www.nhlbi.nih.gov/news/2019/nih-launches-new-collaboration-develop-gene-based-cures-sickle-cell-disease-and-hiv)
50. Dr. Mike McCune on Gene Therapy Insights & Novartis - Gates Foundation, accessed December 16, 2025, [https://www.gatesfoundation.org/ideas/articles/gene-therapy-mike-mccune/](https://www.gatesfoundation.org/ideas/articles/gene-therapy-mike-mccune/)
51. NIH Launches New Collaboration to Develop Gene-Based Cures for Sickle Cell Disease and HIV on Global Scale, accessed December 16, 2025, [https://www.hiv.gov/blog/nih-launches-new-collaboration-develop-gene-based-cures-sickle-cell-disease-and-hiv-global](https://www.hiv.gov/blog/nih-launches-new-collaboration-develop-gene-based-cures-sickle-cell-disease-and-hiv-global)
52. Largest Sickle Cell Study Unlocks Gene Therapy Pathways - The Clinical Trial Vanguard, accessed December 16, 2025, [https://www.clinicaltrialvanguard.com/news/largest-sickle-cell-study-unlocks-gene-therapy-pathways/](https://www.clinicaltrialvanguard.com/news/largest-sickle-cell-study-unlocks-gene-therapy-pathways/)
53. Fifty1 AI Labs repurposes existing drugs to fight sickle cell disease - FirstWord HealthTech, accessed December 16, 2025, [https://firstwordhealthtech.com/story/5989408](https://firstwordhealthtech.com/story/5989408)
54. Intellia Presents Positive Results from the Phase 2 Study of NTLA-2002, an Investigational In Vivo CRISPR Gene Editing Treatment for Hereditary Angioedema (HAE), accessed December 16, 2025, [https://ir.intelliatx.com/news-releases/news-release-details/intellia-presents-positive-results-phase-2-study-ntla-2002](https://ir.intelliatx.com/news-releases/news-release-details/intellia-presents-positive-results-phase-2-study-ntla-2002)
55. Intellia Therapeutics Announces Fourth Quarter and Full-Year 2023 Financial Results and Highlights Recent Company Progress, accessed December 16, 2025, [https://ir.intelliatx.com/news-releases/news-release-details/intellia-therapeutics-announces-fourth-quarter-and-full-year-6](https://ir.intelliatx.com/news-releases/news-release-details/intellia-therapeutics-announces-fourth-quarter-and-full-year-6)
