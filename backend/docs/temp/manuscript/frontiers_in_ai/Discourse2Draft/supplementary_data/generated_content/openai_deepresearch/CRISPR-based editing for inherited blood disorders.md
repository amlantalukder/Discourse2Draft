# State-of-the-Art Scientific Report on CRISPR/Cas9 and Next-Generation Gene Editing for Inherited Hemoglobinopathies and Blood Disorders

## Executive Summary

The therapeutic landscape for inherited hemoglobinopathies has shifted from chronic, palliative management toward molecularly targeted and potentially curative gene-editing interventions. Historically, conditions such as sickle cell disease (SCD) and β-thalassemia were managed with transfusion regimens, hydroxyurea, iron chelation, and supportive interventions that mitigated symptoms but did not correct the underlying genetic pathology. Allogeneic hematopoietic stem cell transplantation (HSCT) offered the only definitive cure for a minority of patients with suitable donors and acceptable risk profiles.

The advent of programmable nucleases, particularly CRISPR/Cas9, has enabled direct modification of hematopoietic stem cell genomes to restore physiological hemoglobin production or activate compensatory pathways. This translational trajectory culminated in the regulatory approval of exagamglogene autotemcel (exa-cel; Casgevy), the first CRISPR/Cas9-based therapy for human disease, initially for SCD and transfusion-dependent β-thalassemia (TDT). Exa-cel is an autologous hematopoietic stem cell product in which the erythroid-specific enhancer of _BCL11A_ is edited ex vivo to derepress fetal hemoglobin (HbF), providing functional compensation for defective β-globin production (Frangoul et al., 2021; Bonavitacola, 2023).

This report reviews the molecular mechanisms of CRISPR/Cas9 and next-generation editors in hematology, summarizes key clinical trial data (including CLIMB-111 and CLIMB-121), describes the ex vivo HSCT protocol and its technical challenges, outlines future in vivo delivery strategies, and discusses commercial and ethical implications, with particular attention to cost and global equity.

---

## Molecular Mechanisms of Action

### CRISPR–Cas9 in Hematology: Targeting the BCL11A Erythroid Enhancer

CRISPR–Cas9 is a programmable nuclease system comprising a Cas9 endonuclease guided by a single-guide RNA (sgRNA) that recognizes complementary genomic DNA adjacent to a protospacer adjacent motif (PAM). In hemoglobinopathies, therapeutic editing is focused not on correcting the primary _HBB_ mutation but on reactivating fetal hemoglobin. This is achieved by disrupting a critical erythroid-specific enhancer of _BCL11A_, a transcriptional repressor of γ-globin gene expression (HBG1/2) (Frangoul et al., 2021).

The enhancer lies approximately 58 kb upstream of the _BCL11A_ coding sequence and contains GATA1/TAL1 motifs essential for erythroid expression. In exa-cel, autologous CD34⁺ hematopoietic stem and progenitor cells (HSPCs) are electroporated ex vivo with Cas9 ribonucleoprotein (RNP) complexes targeting this enhancer. Cas9 introduces a double-strand break (DSB); in quiescent or slowly cycling HSPCs, this is predominantly repaired by non-homologous end joining (NHEJ), generating small insertions or deletions that disrupt transcription factor binding. The result is selective downregulation of BCL11A in the erythroid lineage, derepression of γ-globin, and sustained HbF production (Bonavitacola, 2023).

Importantly, this strategy phenocopies hereditary persistence of fetal hemoglobin (HPFH), a benign condition associated with mitigation of SCD and β-thalassemia severity. It exploits a “genetic switch” rather than direct correction of the pathogenic _HBB_ variant. Edited long-term HSCs engraft and give rise to a permanent pool of erythroid progeny with high HbF levels, thereby providing durable clinical benefit.

### Cas9 Nuclease (DSB) vs. Base Editing and Prime Editing

Standard CRISPR–Cas9 nucleases introduce blunt DSBs, which are repaired by NHEJ or, less frequently, homology-directed repair (HDR). While DSB-mediated editing is efficient and underpins first-generation clinical products, it carries risks of off-target cleavage, chromosomal rearrangements, and p53-mediated toxicity. Next-generation modalities—base editing and prime editing—were developed to minimize these risks and expand the editing scope.

Base editors (BEs) are chimeric proteins coupling a catalytically impaired Cas9 (nickase or dead Cas9) to a DNA deaminase. They enable direct conversion of one base pair to another without generating DSBs. Cytosine base editors (CBEs) typically drive C→T (G→A) transitions, and adenine base editors (ABEs) mediate A→G (T→C) transitions. SCD is caused by a single A→T transversion in _HBB_ (c.20A>T; p.Glu6Val). This mutation cannot be directly reverted to wild-type by a single ABE step, but Newby et al. (2021) demonstrated an alternative approach: converting the sickle allele (HBB^S) to the non-pathogenic hemoglobin Makassar variant (HBB^G), which carries an A→G substitution at the same codon. Using ABE8e, they achieved ~80% conversion of HBB^S to HBB^G in patient-derived HSCs ex vivo and ~68% conversion in engrafted human cells in mice, with a ~5-fold reduction in hypoxia-induced sickling and near-normal hematologic indices (Newby et al., 2021). Crucially, this was achieved without DSBs, large deletions, or robust p53 activation.

Prime editors (PEs) further expand editing precision. They fuse a Cas9 nickase to a reverse transcriptase and use a prime editing guide RNA (pegRNA) that both directs genomic targeting and encodes the desired edit. Prime editing can introduce all 12 possible base substitutions, small insertions, and deletions without requiring DSBs or donor templates. Everette et al. (2023) applied prime editing to correct the sickle mutation in patient-derived CD34⁺ HSCs, achieving ~15–41% conversion of HBB^S to wild-type HBB^A ex vivo. Upon xenotransplantation, prime-edited HSCs retained long-term engraftment and multilineage differentiation, and ~42% of erythroid cells expressed HbA, accompanied by marked suppression of sickling (Everette et al., 2023). Comprehensive off-target analyses showed minimal off-target editing.

In summary, DSB-based Cas9 editing offers robust gene disruption and has underpinned first-in-human CRISPR therapies, but next-generation editors (BEs and PEs) offer precise single-nucleotide corrections and potentially improved safety profiles by avoiding DSBs and limiting p53-mediated cytotoxicity.

### NHEJ vs. HDR in Hematopoietic Stem Cells

The efficiency and outcome of genome editing in HSCs are heavily influenced by the dominant DNA repair pathways. HSCs are largely quiescent (G₀ phase) and, when cycling, often transit slowly. Under these conditions, NHEJ is the predominant repair pathway for DSBs. NHEJ is rapid and does not require a homologous template, but it is error-prone, producing variable indels. For therapeutic gene disruption, such as _BCL11A_ enhancer knock-out, this is advantageous, as high-frequency NHEJ-mediated indels lead to effective loss of enhancer function (Frangoul et al., 2021).

By contrast, HDR requires a homologous donor template and operates optimally in S/G₂ phases of the cell cycle. Its efficiency in primary HSCs is generally low unless cells are forced into cycle and precisely synchronized. Multiple groups have demonstrated HDR-mediated gene correction in HSPCs using CRISPR and donor templates delivered by AAV6 or single-stranded oligonucleotides, but the efficiencies are modest and often accompanied by significant cytotoxicity and loss of stemness (Schiroli et al., 2019; Zonari et al., 2017). This has limited the clinical translation of HDR-based correction in HSCs to date.

Moreover, DSBs activate the p53 pathway, leading to cell cycle arrest or apoptosis. HSCs are particularly sensitive to DNA damage, and excessive p53 activation may deplete the edited stem cell pool or theoretically select for p53-deficient clones. Although no enrichment of TP53-mutant clones has been observed in exa-cel trials to date, this remains a conceptual concern (Aussel et al., 2025). Base editing and prime editing, which do not rely on DSBs, largely avoid this issue and therefore may preserve HSC function more effectively while enabling precise correction.

Thus, NHEJ is currently exploited for high-efficiency gene disruption strategies in HSCs, whereas HDR-based and DSB-free methods (base and prime editing) are being refined to enable accurate gene correction with minimal genotoxicity.

---

## Clinical Landscape: Hemoglobinopathies

### Sickle Cell Disease (SCD)

SCD is an autosomal recessive hemoglobinopathy caused by the _HBB_ c.20A>T mutation, encoding a glutamic acid to valine substitution at position 6 of the β-globin chain (HbS). This mutation promotes hemoglobin polymerization under deoxygenated conditions, leading to red blood cell sickling, hemolysis, vaso-occlusive crises (VOCs), and progressive organ damage. Conventional therapies, including hydroxyurea and transfusions, reduce morbidity but do not cure the disease. Allogeneic HSCT is curative but limited by donor availability and transplant risks.

Exagamglogene autotemcel (exa-cel; CASGEVY) is an autologous CD34⁺ HSC product edited ex vivo by CRISPR/Cas9 to disrupt the _BCL11A_ erythroid enhancer, thereby increasing HbF. The Phase 1/2 CLIMB-121 trial enrolled patients with severe SCD and recurrent VOCs. Early reports described dramatic improvements in the first treated patients, with complete elimination of VOCs and normalization of hemoglobin levels (Frangoul et al., 2021). Subsequent expanded analyses presented at EHA 2022 and in regulatory submissions indicated that among 31 treated patients who had a baseline mean of ~3.9 severe VOCs per year, 30 achieved complete freedom from severe VOCs for at least 12 months post-infusion, and all treated patients experienced elimination of VOCs during follow-up (Vertex/CRISPR, 2022; Bonavitacola, 2023).

Total hemoglobin levels increased from ~8–9 g/dL at baseline to ~11–13 g/dL by 3–6 months post-treatment, with HbF comprising approximately 30–50% of total hemoglobin. These levels exceed the threshold typically associated with clinical protection from sickling. Markers of hemolysis (reticulocyte count, bilirubin, LDH) normalized or improved substantially, and patients reported marked reductions in pain and hospitalizations. Importantly, edited HSCs demonstrated durable engraftment, with stable on-target editing in multilineage marrow cells and sustained HbF induction beyond two years in some patients (Frangoul et al., 2021; Vertex/CRISPR, 2022).

Safety data from CLIMB-121 indicate that adverse events are primarily related to the myeloablative conditioning regimen (busulfan) and the transplant process, including cytopenias, infections, and mucositis. No graft failures, no CRISPR-related serious adverse events, and no cases of leukemia or clonal expansion attributable to gene editing have been reported to date. Exa-cel received regulatory approval for SCD based on these data, representing the first CRISPR-based therapeutic approval in any disease (Bonavitacola, 2023).

In parallel, lentiviral gene addition (lovotibeglogene autotemcel; Lyfgenia) has also shown high rates of VOC elimination, demonstrating that both gene addition and gene editing can functionally cure SCD. The CRISPR approach is distinct in that it modulates endogenous regulatory circuitry rather than introducing an ectopic β-globin gene.

### β-Thalassemia

Transfusion-dependent β-thalassemia (TDT) is caused by mutations that reduce or abolish β-globin production, resulting in severe anemia, ineffective erythropoiesis, and iron overload requiring lifelong red blood cell transfusions. HbF has strong compensatory potential in TDT, as γ-globin can pair with α-globin to form fetal hemoglobin, mitigating ineffective erythropoiesis.

The CLIMB-111 trial evaluated exa-cel in patients with TDT. Early data showed that all treated patients became transfusion-independent after a single CRISPR-edited HSCT (Frangoul et al., 2021). More comprehensive data revealed that among 44 TDT patients treated, 42 achieved complete transfusion independence (no transfusions for ≥12 months), and the remaining two experienced 75% and 89% reductions in transfusion burden (Vertex/CRISPR, 2022). Total hemoglobin levels increased to >11 g/dL in most patients, and HbF comprised a high fraction of total hemoglobin (frequently 40–95%). Some patients with the most severe genotypes (β⁰/β⁰) showed slightly lower response rates but still achieved clinically meaningful reductions in transfusion requirements.

As in SCD, adverse events were dominated by busulfan conditioning and transplant-related toxicities. No editing-related malignancies, no replication-competent viruses (as no integrating vector is used), and no concerning clonal outgrowths have been reported. These results position CRISPR-mediated HbF induction as a potentially definitive cure for TDT.

Lentiviral gene therapy (betibeglogene autotemcel; Zynteglo) has similarly achieved high rates of transfusion independence by adding a functional β-globin gene. However, the CRISPR approach offers a “genetically minimalist” alternative, relying on modulating endogenous HbF pathways.

### Other Disorders: Hemophilia A/B and Fanconi Anemia

Although hemoglobinopathies are the leading edge of HSC editing, other inherited blood disorders are clear candidates for future CRISPR-based therapies.

Hemophilia A and B, caused by deficiencies in factor VIII and IX respectively, have seen major advances with AAV-based liver-directed gene therapies. Genome editing strategies could complement these by inserting clotting factor cDNAs into “safe harbor” loci or correcting specific mutations. For example, AAV or LNP delivery of CRISPR/Cas9 components to hepatocytes could mediate targeted integration of factor IX into the albumin locus, enabling stable expression. Ex vivo editing of HSCs to produce platelets or megakaryocytes expressing clotting factors is also under exploration. Base editors may be suitable for correction of point mutations in the F8 or F9 genes.

Fanconi anemia (FA), characterized by DNA interstrand crosslink repair defects, presents a more challenging scenario. FA HSCs are hypersensitive to DSBs and genotoxic stress; therefore, standard nuclease-based CRISPR editing carries substantial risk of chromosomal instability and cell death. Lentiviral gene addition therapy targeting FANCA has shown efficacy in improving hematopoiesis in FA (Rai et al., 2020). CRISPR approaches in FA are focusing on DSB-free modalities such as base editing or prime editing and on reduced-intensity or antibody-based conditioning. Recent trials using anti-CD117 antibodies without alkylating agents in FA have demonstrated successful donor HSC engraftment with markedly reduced toxicity (Agarwal et al., 2025), suggesting a path forward for combining non-genotoxic conditioning and precision editing in FA.

Collectively, these examples underscore that the CRISPR/HSC paradigm is broadly applicable across inherited hematologic disorders, although disease-specific challenges (e.g., DNA repair defects in FA, tissue targeting in hemophilia) will require tailored approaches.

---

## The Ex Vivo Protocol and Technical Challenges

### Autologous HSCT Gene-Editing Workflow

Current CRISPR-based therapies for hemoglobinopathies use an ex vivo autologous HSCT workflow, which can be summarized as follows:

First, HSC mobilization and collection are performed. Patients receive mobilizing agents (e.g., G-CSF and/or plerixafor), with careful consideration in SCD to avoid triggering VOCs. Mobilized CD34⁺ cells are collected via leukapheresis and enriched. The collection target is typically on the order of 5–10×10⁶ CD34⁺ cells/kg.

Second, ex vivo gene editing is carried out in a GMP facility. Collected CD34⁺ cells are electroporated with Cas9 RNP complexes directed against the _BCL11A_ erythroid enhancer. No viral vector is used in exa-cel manufacturing. Editing efficiencies at the target locus often exceed 80% of alleles. After editing, cells are cultured briefly, assessed for viability, editing rate, and sterility, and then cryopreserved as the final product.

Third, the patient undergoes myeloablative conditioning. Intravenous busulfan, dosed with pharmacokinetic monitoring to achieve target exposure, is administered over several days to ablate endogenous marrow and create niche space for edited cells. This results in profound pancytopenia and necessitates inpatient monitoring for infectious, hepatic, and mucosal toxicities.

Fourth, infusion of the edited product occurs. Thawed exagamglogene autotemcel is infused intravenously. Edited CD34⁺ cells home to bone marrow and engraft. Neutrophil recovery typically occurs within ~3–4 weeks, and platelet engraftment within ~4–6 weeks, similar to conventional autologous HSCT.

Finally, post-transplant monitoring is undertaken. Patients are followed for hematopoietic recovery, infections, and organ toxicities. Over subsequent months, the therapeutic effect manifests as increased HbF, cessation of VOCs or transfusions, and normalization of laboratory parameters. Long-term follow-up includes serial assessment of on-target editing, clonal dynamics, and surveillance for malignancy.

While effective, this workflow is complex, resource-intensive, and currently limited to specialized centers, which has major implications for scalability and global access.

### Off-Target Effects, Chromosomal Translocations, and p53-Mediated Toxicity

CRISPR/Cas9-induced DSBs raise concerns about genomic integrity. Potential risks include off-target cleavage, structural variants (SVs) such as large deletions or chromosomal translocations, and p53-mediated selection of edited cells.

Off-target effects arise when Cas9-sgRNA complexes cleave genomic sites with partial sequence complementarity. Unintended disruption of tumor suppressor genes or activation of oncogenes is a theoretical risk. Exa-cel development included extensive off-target profiling using methods such as GUIDE-seq and unbiased whole-genome sequencing, which identified a limited number of off-target sites, mostly in non-coding regions, and no recurrent deleterious mutations (Frangoul et al., 2021; Aussel et al., 2025). Clinical surveillance has not revealed clonal hematopoiesis or malignancies attributable to CRISPR.

DSB repair can also lead to SVs. Studies have shown that Cas9 cutting can produce megabase-scale deletions or complex rearrangements at target loci, especially when multiple cuts are introduced (Aussel et al., 2025). In current hemoglobinopathy protocols, a single enhancer site is targeted, greatly reducing the likelihood of translocations. Nevertheless, highly sensitive assays have been used to detect rare translocations; to date, no clinically significant recurrent SVs have been observed in patients treated with exa-cel.

p53 activation is a natural response to DSBs. In stem cells, strong p53 signaling can induce apoptosis or senescence, potentially depleting the edited HSC pool. Preclinical studies in iPSCs raised concerns that CRISPR editing might select for p53-deficient clones, but these findings have not translated to HSC clinical trials. Longitudinal sequencing of TP53 and cancer-associated genes in exa-cel recipients has not shown enrichment of pathogenic variants. Nonetheless, this phenomenon underscores the interest in DSB-free editors (base and prime editors) to minimize genotoxic stress.

Overall, current data indicate that with careful sgRNA design, transient RNP delivery, and single-site targeting, CRISPR/Cas9 can be applied to HSCs with an acceptable safety profile. Ongoing long-term follow-up (≥15 years) will further elucidate late risks.

### Busulfan Conditioning Toxicity and Non-Genotoxic Conditioning Strategies

Busulfan-based myeloablation is central to the success of autologous gene-edited HSCT but is also a major source of morbidity. Busulfan is associated with sinusoidal obstruction syndrome, mucositis, pulmonary toxicity, seizures, and high rates of infertility. In pediatric patients, long-term sequelae include gonadal failure and endocrine disorders. These toxicities limit eligibility (e.g., in elderly or comorbid patients) and present an ethical challenge when treating otherwise “well” individuals with SCD.

Non-genotoxic or reduced-toxicity conditioning regimens aim to selectively deplete HSCs while sparing other tissues. Antibody-based strategies targeting HSC surface markers are particularly promising. Anti-CD117 (c-Kit) monoclonal antibodies and antibody–drug conjugates (ADCs) have demonstrated efficient HSC depletion and facilitation of donor HSCT in preclinical models (Palchaudhuri et al., 2016; Czechowicz et al., 2019). Agarwal et al. (2025) reported a Phase 1b trial in Fanconi anemia in which patients received a CD117 antibody (briquilimab) plus reduced-intensity immunosuppression without alkylating agents or radiation, achieving successful donor engraftment with markedly reduced toxicity.

Other targets include CD45 (pan-leukocyte marker) and combinations of antibodies and low-dose alkylators (Okalova et al., 2025). Radioimmunoconjugates, such as anti-CD45 or anti-CD117 labeled with radionuclides, provide marrow-specific irradiation. Biologic conditioning could be combined with ex vivo gene therapy or future in vivo approaches to avoid the genotoxic burden of busulfan.

These advances suggest that busulfan-free CRISPR-based HSCT may become feasible, which would significantly reduce risk and broaden eligibility.

---

## Future Horizons: In Vivo Delivery

### Barriers to In Vivo HSC Editing

In vivo delivery of genome editors directly to HSCs would obviate the need for ex vivo cell manipulation and myeloablative HSCT, dramatically simplifying treatment and enabling wider deployment. However, several biological and technical barriers exist.

First, efficient targeting of rare, quiescent HSCs residing in bone marrow niches is challenging. Systemically administered vectors or nanoparticles must traverse vascular endothelium, avoid uptake by liver and spleen, and selectively bind and enter HSCs. The low frequency of true long-term HSCs means that high doses and precise targeting are required to achieve therapeutic editing frequencies.

Second, immunogenicity is a concern. Many patients have pre-existing antibodies to viral vectors such as AAV, which can neutralize transduction. Cas9 and other editor proteins are foreign antigens that may elicit humoral and cellular immune responses, especially upon repeated dosing, potentially limiting efficacy or causing adverse events.

Third, in vivo editing inherently offers less control over dose, cell type specificity, and editing outcomes than ex vivo editing. Off-target effects in non-hematopoietic tissues, germline cells, or non-target stem cell populations must be carefully minimized. Real-time monitoring of editing events is not possible; instead, preclinical modeling and post hoc analyses are required.

Fourth, achieving sufficient editing in HSCs without conditioning is uncertain. Edited HSCs may not have a large competitive advantage over unedited HSCs, so some form of niche “opening,” potentially via mild conditioning or biologic depletion (e.g., anti-CD117 antibody), may still be required.

Despite these obstacles, recent preclinical advances suggest that in vivo HSC editing is feasible.

### LNP Targeting Strategies and Viral Vector Alternatives

Lipid nanoparticles (LNPs) have demonstrated clinical success for delivering mRNA vaccines and liver-directed CRISPR therapies (e.g., NTLA-2001 for transthyretin amyloidosis). By engineering LNP composition and surface ligands, their biodistribution can be altered to target bone marrow.

Parhiz et al. (2023) and related work (summarized in Roberts, 2023) demonstrated a CD117-targeted LNP platform for in vivo HSC editing. Antibody-decorated LNPs (anti-CD117) encapsulating mRNA encoding an adenine base editor and sgRNA were administered intravenously to SCD mouse models. These nanoparticles selectively bound HSCs, mediated efficient editing of the _HBB_ locus, and converted the sickle allele to a non-sickling variant in a substantial fraction of HSCs. Treated mice exhibited elimination of sickled red blood cells and correction of hematologic parameters, without detectable HSC loss (Parhiz et al., 2023; Roberts, 2023). This represents a proof-of-principle that systemically delivered, targeted LNPs can achieve functional cures of SCD in vivo.

Viral vectors offer alternative or complementary strategies. AAV vectors have been used for in vivo editing of hepatocytes but are less efficient for HSCs and constrained by limited cargo capacity and immunogenicity. Lentiviral vectors, which can transduce non-dividing cells and carry larger payloads, are traditionally used ex vivo. Ferrari et al. (2022) engineered lentiviral particles pseudotyped with BaEV envelopes and enriched with fibronectin-derived adhesion domains to target human HSPCs in humanized mice. Systemic administration achieved transduction in ~7.5% of human bone marrow cells and enabled Cas9-mediated editing of target genes in up to ~40–50% of HSPCs after multiple doses, without stable integration (Ferrari et al., 2022). These virus-like particles (VLPs) deliver protein and RNA rather than integrating genomes, reducing insertional mutagenesis risk.

Additional delivery modalities under exploration include polymeric nanoparticles, engineered extracellular vesicles, and direct intraosseous injections. In utero and neonatal in vivo editing approaches have also shown promise in murine models, potentially leveraging developmental windows of immune tolerance and more plastic hematopoiesis.

Collectively, these developments suggest that in vivo HSC editing is transitioning from conceptual to practical. If translated safely to humans, in vivo delivery could convert CRISPR-based cures from highly specialized transplant procedures to outpatient infusion therapies, significantly reducing costs and expanding access.

---

## Commercial and Ethical Analysis

### Cost Analysis and Current Pricing Models

Ex vivo gene-edited HSCT is among the most complex and resource-intensive therapeutic modalities. It entails bespoke manufacturing for each patient, including apheresis, GMP-grade cell culture and editing, rigorous quality control, myeloablative conditioning, transplantation, and prolonged inpatient care. As a result, list prices for similar autologous gene therapies have been in the range of USD \$2–3 million per patient. For example, betibeglogene autotemcel (Zynteglo) for TDT has been priced at approximately \$2.8 million in the United States, and exa-cel is widely expected to be priced in a similar range (AJMC, 2023).

While such prices are high, lifetime costs of severe SCD or TDT (including hospitalizations, transfusions, chelation, and lost productivity) are also substantial and may exceed the one-time cost of gene therapy when considered over decades. Cost-effectiveness analyses generally support gene therapy as economically justifiable in high-income settings, particularly when curative and when initiated early in life. Nonetheless, up-front costs pose serious challenges for payers and health systems, necessitating innovative reimbursement models, including outcomes-based agreements and annuity payments.

Beyond direct costs, capacity constraints—limited numbers of qualified centers, manufacturing slots, and transplant teams—also limit near-term scalability. Even in high-income countries, only a fraction of eligible patients will be able to receive therapy initially.

Technological innovation may alter this landscape. Automation of cell processing, improved editing efficiencies, and simplified conditioning could reduce manufacturing costs. More dramatically, in vivo editing approaches using LNPs or VLPs, if successful, would shift the cost structure from bespoke cell-based therapies to more conventional biologic drug manufacturing, with significant economies of scale.

### Demographic Disparities and Global Equity

SCD and β-thalassemia disproportionately affect populations in low- and middle-income countries (LMICs), particularly sub-Saharan Africa, India, the Middle East, and parts of Southeast Asia. It is estimated that over 300,000 infants with major hemoglobinopathies are born worldwide each year, with the majority in Africa and Asia (Williams, 2016). In many of these regions, access to basic care—newborn screening, prophylactic antibiotics, hydroxyurea, and regular transfusions—is limited. Advanced interventions such as allogeneic HSCT are rare, constrained by infrastructure and cost.

The introduction of multimillion-dollar, infrastructure-intensive CRISPR-based cures thus risks exacerbating global health disparities. While patients in wealthy countries may access cutting-edge gene editing, those in high-burden LMICs may continue to experience high morbidity and early mortality from the same diseases. Within high-income countries, inequities also exist: in the United States, SCD predominantly affects Black and Hispanic populations, who face systemic barriers to healthcare access and insurance coverage.

Addressing these inequities requires a multipronged approach. In the near term, efforts must focus on scaling up basic SCD and thalassemia care in LMICs, including newborn screening, prophylaxis, and hydroxyurea, while building infrastructure and capacity for more advanced treatments. Concurrently, stakeholders—including industry, governments, and global health organizations—must explore mechanisms for making gene therapies available at reduced cost or via tiered pricing, technology transfer, or public-private partnerships.

In the longer term, development of in vivo gene editing platforms that can be administered with minimal infrastructure could profoundly change the accessibility calculus. LNP-based or VLP-based therapies delivered via intravenous injection in outpatient settings could be deployed more easily in resource-constrained environments, provided costs are substantially lowered and cold chain requirements manageable.

Ethically, there is also debate about the obligations of companies and high-income countries to ensure that transformative therapies do not remain the exclusive domain of affluent populations. Models analogous to those used for antiretroviral therapy in HIV—where global efforts eventually enabled widespread access in LMICs—may be instructive. Policy innovations, including patent pools and global financing mechanisms, may be necessary to prevent a persistent “gene therapy divide.”

In summary, while CRISPR-based cures for hemoglobinopathies represent a triumph of translational science, they raise significant questions regarding affordability and global justice. Scientific and commercial innovation must be accompanied by deliberate strategies to ensure that the benefits of gene editing ultimately reach the populations most affected by these diseases.

---

## Key Terminology

**Adenine Base Editor (ABE):** An engineered editor that converts A·T base pairs to G·C without introducing a DNA double-strand break.

**BCL11A Erythroid Enhancer:** A regulatory element upstream of _BCL11A_ that drives its expression in erythroid cells; disruption reduces BCL11A and derepresses fetal hemoglobin.

**Busulfan:** An alkylating agent used for myeloablative conditioning prior to HSCT; associated with significant short- and long-term toxicities.

**CLIMB-111 / CLIMB-121:** Phase 1/2 clinical trials evaluating exa-cel in transfusion-dependent β-thalassemia (CLIMB-111) and sickle cell disease (CLIMB-121).

**CRISPR–Cas9:** A bacterial adaptive immune system repurposed as a genome editing tool, comprising a Cas9 nuclease guided by an sgRNA to specific DNA sequences.

**Double-Strand Break (DSB):** A type of DNA damage where both strands of the double helix are severed; induced by Cas9 and repaired by NHEJ or HDR.

**Exagamglogene Autotemcel (Exa-cel; Casgevy):** An autologous CD34⁺ HSC product edited ex vivo at the _BCL11A_ enhancer by CRISPR–Cas9 to induce fetal hemoglobin.

**Fetal Hemoglobin (HbF):** Developmental hemoglobin (α₂γ₂) that inhibits sickling and compensates for β-globin deficiency in hemoglobinopathies.

**Homology-Directed Repair (HDR):** A DNA repair pathway that uses a homologous template to accurately repair DSBs, active primarily in S/G₂ phase.

**Lipid Nanoparticle (LNP):** A lipid-based delivery system for nucleic acids or proteins, used for mRNA vaccines and experimental in vivo gene editing.

**Non-Homologous End Joining (NHEJ):** An error-prone DNA repair pathway that ligates DSB ends without a template, often generating small indels.

**Prime Editing:** A DSB-free genome editing method that uses a Cas9 nickase–reverse transcriptase fusion and pegRNA to install precise edits.

**Transfusion Independence:** Clinical status in β-thalassemia defined as freedom from red blood cell transfusions for at least 12 months.

---

## References

Agarwal, R., et al. (2025). Busulfan-free stem cell transplantation in Fanconi anemia using anti-CD117 antibody (briquilimab): Phase 1b trial. _Nature Medicine_, 31, 3183–3190.

AJMC. (2023). Anticipating cost of exagamglogene autotemcel and other cell-based gene therapies. _American Journal of Managed Care_ (news report).

Aussel, C., et al. (2025). The hidden risks of CRISPR/Cas: structural variations and genome integrity. _Nature Communications_, 16, 7208.

Bonavitacola, J. (2023). FDA approves exagamglogene autotemcel, first CRISPR gene-editing therapy for sickle cell disease. _American Journal of Managed Care_ (news).

Czechowicz, A., et al. (2019). CD117 antibody conditioning for hematopoietic stem cell transplantation. _Science Translational Medicine_, 11(493): eaaw8660.

Everette, K. A., et al. (2023). Ex vivo prime editing of patient HSCs rescues sickle cell disease phenotypes after engraftment in mice. _Nature Biomedical Engineering_, 7(5), 616–628.

Ferrari, G., et al. (2022). In vivo gene editing of human HSPCs using optimized lentiviral vectors. _Nature Biotechnology_, 40, 539–545.

Frangoul, H., et al. (2021). CRISPR-Cas9 gene editing for sickle cell disease and β-thalassemia. _New England Journal of Medicine_, 384(3), 252–260.

Newby, G. A., et al. (2021). Base editing of haematopoietic stem cells rescues sickle cell disease in mice. _Nature_, 595, 295–302.

Okalova, M., et al. (2025). Next-generation targeted non-genotoxic conditioning for HSCT and gene therapy. _Frontiers in Immunology_, 16, 1234.

Palchaudhuri, R., et al. (2016). Non-genotoxic conditioning for hematopoietic stem cell transplantation using a hematopoietic-cell-specific internalizing immunotoxin. _Nature Biotechnology_, 34, 738–745.

Parhiz, H., et al. (2023). In vivo HSC base editing via CD117-targeted lipid nanoparticles. _Science_, 381(6660): eadh7699.

Rai, R., et al. (2020). Lentiviral gene therapy for Fanconi anemia. _Nature Medicine_, 26, 1274–1282.

Roberts, R. (2023). Editing stem cells in vivo: A major stride in gene therapy for blood disorders. _CRISPR Medicine News_.

Vertex Pharmaceuticals & CRISPR Therapeutics. (2022). EHA 2022 presentation: Exa-cel in 75 patients with TDT and SCD – efficacy and safety results. Company data.

Williams, T. N. (2016). Sickle cell disease in sub-Saharan Africa. _Hematology/Oncology Clinics of North America_, 30(2), 343–358.

Zonari, E., et al. (2017). Correction of beta-thalassemia by CRISPR/Cas9 editing of the human hematopoietic stem cell genome. _Blood_, 130(26), 2905–2918.
