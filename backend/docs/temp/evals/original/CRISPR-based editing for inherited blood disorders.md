# CRISPR-based therapeutic genome editing for inherited blood disorders

**Abstract**

Therapeutic genome editing promises to transform medicine. Pivotal discoveries have provided a diverse and versatile set of tools to correct pathogenic mutations or produce protective alleles using CRISPR-based technologies. These innovative therapies are especially adaptable for blood and immune disorders, where clinical methods allow haematopoietic stem cells (HSCs) to be mobilized, harvested, engineered ex vivo and transplanted back into a patient to permanently replace their blood system. This paradigm has been exemplified with the first US Food and Drug Administration (FDA)-approved CRISPR–Cas9 therapy for sickle cell disease and β-thalassaemia, exa-cel (Casgevy). Although promising, efficient delivery of gene edits involves complicated ex vivo manipulation and toxic myeloablative conditioning. The quiescent and elusive nature of HSCs also brings associated challenges. In this Review, we explore the state-of-the-art genome editing technologies of nucleases, base editors and prime editors, which hold promise to address unmet clinical needs for patients with inherited haematological disorders. We highlight the progress made for several disorders and discuss the challenges that remain for ex vivo and in vivo targeting of HSCs for next-generation gene therapies.

## Introduction

The discovery of programmable RNA-guided nucleases from prokaryotic antiviral systems1,2,3 sparked a revolution in molecular biology and medicine. In their natural habitat, CRISPR systems provide acquired resistance to bacteriophages or mobile genetic elements via RNA-mediated recognition of invading nucleic acid sequences, leading to rapid cleavage by the CRISPR-associated Cas nuclease2,4. Thanks to their ease of programmability, CRISPR–Cas enzymes were repurposed to precisely install DNA double-strand breaks (DSBs) at diverse genomic loci in human cells5,6. The portability of CRISPR–Cas nucleases to eukaryotic cells offered a wealth of opportunities to permanently rectify diverse genetic disorders by therapeutic genome editing. To realize the therapeutic potential of genome editors, safe and efficient genetic modification must be completed with minimal genotoxic effects. Although efficient sequence disruption is readily achieved in human cells, reaching therapeutic levels of precise gene correction has been more challenging. New CRISPR-based technologies, such as base and prime editors, now offer the possibility of installing small genetic modifications without requiring DSBs7,8,9. These technologies could prove to be more precise than nuclease-driven genome editing. Building on these pivotal scientific developments, the ever-growing CRISPR toolkit could address unmet clinical needs for patients afflicted with genetic disorders.

Inherited haematological disorders are leading targets among monogenic diseases that could be amenable to therapeutic genome editing. Blood is an accessible tissue where haematopoietic stem and progenitor cells (HSPCs) can be temporarily mobilized from the bone marrow to the peripheral blood, collected by apheresis and CD34+ selection, engineered ex vivo and cryopreserved. After reinfusion into the blood, engineered haematopoietic stem cells (HSCs) can repopulate the bone marrow to provide a permanent source of healthy haematopoietic cells as a potential lifelong cure for diverse blood disorders. Among them, sickle cell disease (SCD) and transfusion-dependent β-thalassaemia (TDT), caused by mutations in the HBB gene, are the most common inherited blood disorders worldwide with more than 300,000 patients diagnosed annually10,11,12. Erythroid-specific deficiency of BCL11A, a direct repressor of fetal haemoglobin (HbF) expression, has been shown to rescue pathologic features of β-haemoglobinopathies11,13,14,15,16,17. These fundamental discoveries led to the development of a CRISPR-based strategy to disrupt the +58 erythroid-specific enhancer of BCL11A in HSPCs to restore HbF expression16,18,19,20. This approach eliminated vaso-occlusive episodes or the need for transfusions in many patients with SCD and TDT, respectively12, leading to the first US Food and Drug Administration (FDA)-approved CRISPR–Cas9 therapy, exagamglogene autotemcel (exa-cel; Casgevy) (Box 1). This new paradigm in molecular medicine could potentially be extended to other blood and immune disorders, including but not limited to inherited bone marrow failure syndromes21, immunodeficiencies22,23,24,25, lysosomal storage diseases26 and even acquired diseases such as HIV infection27,28.

This Review discusses recent advances towards the development of CRISPR-based therapies for inherited blood disorders, highlighting primary obstacles that hinder safe and efficient gene editing in HSPCs. Gene therapies of HSPCs for inherited blood disorders using integrating viral vectors have been reviewed elsewhere29,30 and are minimally discussed. Although new genome editing platforms are emerging, such as recombinase-based31,32 and epigenome editing33,34, here we focus on nucleases, base editors and prime editors, which have been successfully used in HSPCs and extensively characterized in terms of genotoxicity. We present selected examples of therapeutic genome editing strategies developed for three groups of inherited blood disorders. We note that many other inherited blood disorders, including primary immunodeficiencies and bone marrow failure syndromes, could also warrant consideration for therapeutic genome editing, but a detailed discussion of these conditions falls beyond the scope of this Review. We point out potential pitfalls related to the complexity of HSC biology and attempt to connect lessons learned to overcoming these key challenges. Finally, we discuss potential directions to improve broad patient access to state-of-the-art gene and cell therapies.

## Genome editing technologies

The first proof of concept for mammalian genome editing was demonstrated 31 years ago when Rouet et al. introduced DNA DSBs in mouse cells using the rare-cutting endonuclease I-SceI35. Because chromosomal DSBs must be repaired, this landmark work provided evidence that targeted DSBs could generate small insertions and deletions (indels) via non-homologous end joining (NHEJ) and, in the presence of a DNA donor, could stimulate homologous recombination35 (Fig. 1a). Two years later, the first designer nucleases were engineered by fusing zinc finger proteins to the cleavage domain of the FokI endonuclease36, allowing genome editing in human cells37,38. The therapeutic potential of zinc finger nucleases in haematopoietic cells was demonstrated by targeting a corrective complementary DNA to the IL2RG locus for X-linked severe combined immunodeficiency (X-SCID) in HSPCs39, or disrupting CCR5 in T cells40,41. After breaking the DNA-binding code of transcription activator-like effectors (TALEs) from Xanthomonas42,43, TALE proteins were also fused to the catalytic domain of FokI to generate designer nucleases for genome editing in human cells44. Together, zinc finger and TALE nucleases paved the way for therapeutic genome editing of HSPCs to remedy severe blood disorders. Although promising, these first-generation and second-generation technologies required extensive protein engineering to achieve efficient targeted genome modification. The discovery of readily programmable RNA-guided CRISPR–Cas nucleases ignited the field of therapeutic genome editing.

### CRISPR–Cas nucleases

The evolutionary arms race between bacteria and their viruses, also known as bacteriophages, provides powerful tools for molecular biology. CRISPR–Cas systems are adaptive immune systems present in ~85% and ~40% of archaeal and bacterial genomes, respectively45. These diverse bacteriophage defence systems come with different characteristics, and Class 2 systems have been widely engineered for biotechnology applications due to their single-protein effector module45,46,47. Streptococcus pyogenes Cas9 (SpCas9) is the most widely used and characterized nuclease for therapeutic genome editing (Fig. 1a). SpCas9 genome binding depends on the initial recognition of its NGG protospacer-adjacent motif (PAM), which triggers DNA strand separation to initiate base pairing between the 20 nucleotide single-guide RNA (sgRNA) spacer and the targeted genomic site48,49. Upon sufficient Watson–Crick base pairing, the nuclease undergoes conformational activation and introduces a DNA DSB via its HNH and RuvC catalytic domains50,51. Nuclease-driven DSBs are primarily repaired by end joining mechanisms via direct ligation of the two DSB ends with or without end processing52. Although the latter would restore the SpCas9 recognition sequence, end processing and repair through NHEJ or microhomology-mediated end joining (MMEJ) can lead to indels (Fig. 1a), disrupting the target site and preventing successive rounds of nuclease cleavage52. As NHEJ takes place with rapid kinetics throughout the cell cycle53,54, nuclease-driven genome editing enables highly efficient gene disruption in human cells, including in quiescent HSPCs18,55.

Therapeutic genome editing employing the widely used SpCas9 nuclease is constrained by the requirement for an NGG PAM, and its large size (≈4.1 kb) also poses challenges for in vivo delivery. Smaller CRISPR–Cas nucleases, including but not limited to SaCas9, St1Cas9, NmeCas9 and Cas12a (Cpf1), have been adopted to facilitate in vivo delivery via a single adeno-associated virus (AAV) and to expand the targeting range of CRISPR–Cas systems through alternative PAM sequences56,57,58,59,60. The expanded CRISPR toolkit could also offer alternatives in cases of pre-existing adaptive immunity61. Although the field has leveraged the biological diversity of natural CRISPR–Cas systems, the high efficiency of SpCas9 has also motivated engineering efforts to expand its targeting range. Rational structure-guided engineering and phage-assisted continuous evolution campaigns have led to the development of multiple SpCas9 variants with altered PAM sequences62,63,64,65. Notably, these engineering efforts led to the SpG variant (NGN PAM) and SpRY, the first ‘deprogrammed’ SpCas9 variants that can accept almost all NNN PAMs, although NYN (where Y is C or T) PAMs are less effective66,67. Finally, extensive efforts have enabled the generation of high-fidelity variants with improved specificity68,69,70, including HiFi Cas9, which has enabled highly efficient and precise gene editing in HSPCs when delivered as a ribonucleoprotein (RNP) complex71. Collectively, these scientific advances have significantly expanded the CRISPR toolkit available for therapeutic genome editing.

Targeting a therapeutic transgene of interest to a specific genomic locus to complement a defective gene holds promise for diverse blood disorders. Co-delivering a DNA donor with SpCas9 allows for precise modifications or the integration of a transgene through homology-directed repair (HDR)52 (Fig. 1a). One of the main limitations of HDR is its dependence on DNA end resection, which occurs with slower kinetics than NHEJ and is limited to S and G2 phases of the cell cycle52,53. Because long-term engrafting HSCs (LT-HSCs) are mostly quiescent, this cell cycle limitation poses challenges for maintaining long-term engraftment of HDR-edited HSCs72,73,74,75. This obstacle among others — such as the toxicities of the template donor, the electroporation and the cellular response to DSBs — was highlighted by the CEDAR clinical trial for SCD, which was paused following a serious adverse event of pancytopenia after the first patient was dosed76. Of importance, the HDR donor was co-delivered via AAV6 transduction, which potentially increased cytotoxicity compared with NHEJ-based methods77. Genome editing with AAV donor templates has also been linked to unintended on-target integrations of concatemers and inverted terminal repeats, which are challenging to detect with standard genotyping methods78,79. Alternative HDR donor templates, such as linear single-stranded DNA (ssDNA)73,80, circular single-stranded DNA (cssDNA)81 and integrase-defective lentiviral vector (IDLV)77, have also been successfully used in HSPCs. Altogether, although progress has been made to improve HDR in HSPCs, technologies that take advantage of cellular DNA repair pathways active throughout the cell cycle could facilitate therapeutic genome editing of quiescent LT-HSCs in situ.

### Base editors

Early in the CRISPR craze, it became evident that a catalytically inactive Cas9 (dCas9) could be fused to proteins of interest to target them to specific genomic loci without introducing DSBs82,83,84,85. Building on this, two different groups engineered fusions of an APOBEC1 or PmCDA1 cytidine deaminase with dCas9 to perform targeted DNA base editing installing C•G to T•A substitutions without DSBs7,86 (Fig. 1b). A key limitation of cytosine base editing (CBE) is the generation of a U•G intermediate recognized by uracil DNA glycosylase inhibitor (UGI), which catalyses removal of U and initiates base excision repair (BER). To overcome this issue, a small UGI inhibitor protein from Bacillus subtilis bacteriophage PBS1 was fused to the cytosine base editor. Additionally, the HNH domain of Cas9 was restored (SpCas9-D10A nickase) so that it could nick the non-edited strand to preferentially resolve the U•G into the desired T•A substitution7. The resulting BE3 editor achieved efficient C•G to T•A editing by introducing a single-strand break (SSB).

Half of the known pathogenic point mutations in humans are caused by spontaneous cytosine deamination resulting in C•G to T•A transitions8. To potentially correct these pathogenic mutations, researchers engineered an adenine deaminase for programmable A•T to G•C base editing8. Protein evolution of an Escherichia coli transfer RNA adenosine deaminase (TadA) yielded an enzyme able to catalyse adenine deamination to inosine on DNA substrates8 (Fig. 1b). Whereas uracil intermediates are readily recognized and removed from DNA via BER, inosine intermediates are inefficiently repaired, and no BER inhibitors are needed for efficient adenine base editing (ABE)8.

A key feature of base editors is their editing window. Structural studies of SpCas9 primed for DNA cleavage revealed that the PAM-distal nucleotides of the non-targeted DNA strand are disordered87, releasing a stretch of ssDNA accessible for deaminases upon target recognition. Standard-window base editors usually target nucleotides at positions 4–8 of the non-targeted DNA strand (based on the 5′ position of the protospacer numbered 1) and multiple variants with narrower or wider editing windows have been developed, as reviewed elsewhere88. Therapeutic base editing thus depends on the identification of the right variant and spacer to install the substitution of interest without modifying proximal bystander bases, although additional silent bystander mutations can be tolerated in some cases.

A key challenge for therapeutic base editing is the evaluation of complex off-target activities. All base editors can introduce sgRNA-dependent off-targets, but CBE also induces genome-wide sgRNA-independent off-targets, likely caused by the overexpression of a cytidine deaminase89,90,91. In addition, both CBE and ABE can induce transcriptome-wide guide RNA (gRNA)-independent deamination of RNA92,93. Also, nicks can occasionally be converted to DSBs94. Further engineering efforts have improved the efficiency and specificity of base editors, yielding state-of-the-art CBE and ABE with optimized architectures, evolved deaminases and lower RNA off-target activity92,93,95,96,97,98,99,100,101. Overall, these engineered enzymes allow highly efficient base editing in HSPCs with few DSBs19,102,103,104. Although promising, therapeutic base editing of HSPCs is limited by the editing window, the presence of bystander edits and the nucleotide substitution capabilities of base editors. Hence, many inherited blood disorder mutations are not candidates for correction by current base editing platforms.

### Prime editors

Rewriting genetic codes without DSBs could potentially correct pathogenic mutations caused by base transversions between purine and pyrimidines, as well as small indels. To expand the genome editing toolkit, a genome rewriting enzyme was engineered by fusing the SpCas9-H840A nickase with the Moloney murine leukaemia virus (MMLV) reverse transcriptase9 (Fig. 1c). Appending a 3′ extension harbouring a primer binding site (PBS) and a reverse transcriptase template (RTT) to the sgRNA allowed priming and targeted reverse transcription in human cells9 (Fig. 1c), a process reminiscent of template-primed reverse transcription105. Known as prime editing, this versatile technology allows the installation of small indels and all possible nucleotide substitutions. One key challenge is the permanent incorporation of the edit encoded on the 3′ DNA flap intermediate into the genome. As the prime editing-synthesized flap triggers DNA mismatch repair (MMR)106,107, the original sequence is easily restored when using the strategy known as prime editing 2 (PE2) where only one SSB is introduced (Fig. 1c). Co-delivering an additional nick sgRNA to install a second SSB on the opposite DNA strand biases DNA repair towards incorporating the modification of interest, a strategy denoted as PE3 (ref. 9) (Fig. 1c). Although this approach substantially improves prime editing efficiency, it induces staggered DSBs, which come at the cost of increased small indels, tandem duplications, and rare events of translocations and LINE-1 retrotransposon insertions9,106,108,109. Alternatively, the PE3b strategy9 uses a nick sgRNA that matches the edited strand rather than the original allele to prevent concurrent SSBs and reduce the unwanted consequences of DSBs.

During MMR, DNA mismatches and insertion–deletion loops are first recognized by the MutSα (MSH2–MSH6) or MutSβ (MSH2–MSH3) heterodimers, respectively110,111. MSH2 then recruits the MutLα (PMS2–MLH1) heterodimer, an endonuclease that catalyses the incision of the nicked DNA strand around the mismatched heteroduplex112. In the final steps, EXO1 excises the heteroduplex, polymerase δ synthesizes the excised DNA strand and Ligase 1 seals the nascent strand113,114,115. A dominant-negative hMLH1 protein can be co-delivered to inhibit MMR with (PE5) or without (PE4) a nick sgRNA106. However, co-delivering dominant-negative hMLH1 as mRNA does not appear to improve editing efficiency in HSPCs116,117. Moreover, cellular inhibition of MMR could be mutagenic, as recently reported with increased off-target indels at low-complexity genomic regions in mouse embryos118. Alternatively, incorporating additional silent mutations near the intended edit106,119 or introducing C•C mismatches, which are resistant to MMR120,121,122, markedly improves prime editing efficiency at multiple loci in HSPCs117. Strikingly, editing efficiency at the B2M gene in HSPCs rose from an average of 2% to 25% and 57% with one and two C•C mismatches, respectively117. This simple MMR-evading approach allows highly efficient prime editing with prodigious product purity in HSPCs117, bypassing the need for staggered DSBs. These edits with several mismatches could be suitable for recoding regulatory elements and correcting mutations, along with silent mutations to boost efficiency, but they constrain flexibility to discretely edit single nucleotide variants throughout the genome.

The latest generation prime editor, PE7, a fusion between PEmax106 and the small RNA-binding exonuclease protection factor La (Fig. 1c), also improves editing efficiency in HSPCs without an additional nick sgRNA by stabilizing the prime editing guide RNAs (pegRNAs)123. Although the exact mechanism by which La enhances prime editing is not yet fully elucidated, PE7 functionally interacts with the 3′ polyuridine tracts and likely protects La-accessible pegRNAs from exonuclease degradation123. Given the challenges in producing long GMP-grade synthetic RNAs, such as engineered pegRNAs (epegRNAs) harbouring a structural protection motif124, using PE7 in combination with shorter La-accessible pegRNAs could facilitate clinical translation.

The possibility of rewriting DNA offers opportunities to recode exon-sized sequences. Although standard prime editing is limited to small genetic changes, paired pegRNA strategies, such as twin prime editing (TwinPE), have been developed to integrate larger modifications (30–250 bp) or deletions (<10 kb) by synthesizing complementary flaps on opposite DNA strands125,126,127,128,129 (Fig. 1c). As TwinPE does not produce heteroduplexes that engage MMR125, this approach likely evades MMR by design. Of importance, highly efficient TwinPE was observed when modulating nucleotide metabolism in quiescent HSPCs that were not stimulated with cytokine culture prior to electroporation117. Although the activity of prime editing systems during different phases of the cell cycle has yet to be determined extensively, TwinPE potentially occurs efficiently throughout the cell cycle, which could enable efficient therapeutic genome editing in LT-HSCs. However, the cellular response of HSCs to different prime editing systems is not fully understood. The genotoxic effects of TwinPE-induced staggered DSBs should be thoroughly characterized, because installing these larger modifications via concurrent SSBs could come at the cost of unwanted indels or larger deletions at the target site and inducing a p53 response.

### Emerging CRISPR-based platforms for targeted transgene integration

Achieving safe and efficient targeted therapeutic transgene integration in HSCs is no easy task. Approaches that couple prime editing-mediated installation of a recombinase landing pad into the genome with the introduction of a recombinase to precisely integrate large DNA sequences hold potential for gene therapy. Denoted as PASSIGE125,130 and PASTE131, these two-step methods are based on the installation of attB or attP landing pads via prime editing followed by transgene integration using Bxb1 recombinase, allowing the integration of large DNA cargoes greater than 5 kb in human cells. In PASTE, the Bxb1 recombinase is fused to the carboxy-terminal region of the prime editor, whereas in PASSIGE the two components are delivered individually125,128,130,131. Because Bxb1 tethering to PEmax decreases prime editing efficiency, co-delivering the prime editor and the recombinase separately improves site-specific integrations130. Although progress has been made with evolved Bxb1 recombinases130,132, therapeutic transgene integration has yet to be achieved in HSCs. Other emerging platforms include CRISPR-associated transposases88,133. In their current form, recombinase and transposase modalities depend on plasmid donors, which are highly toxic in primary haematopoietic cells. Because naked double-stranded DNA (dsDNA) can trigger pattern recognition receptor pathways such as the cGAS–STING pathway, co-delivering a dsDNA donor induces cell death in HSCs134,135. Alternatively, ssDNA and cssDNA donors have limited immunogenicity and are thus better tolerated in HSCs73,80,81,134. Given this immunological barrier, genome editing modalities that rely on ssDNA donors or evade dsDNA sensing might improve targeted therapeutic transgene integration in HSCs.

## Therapeutic opportunities for haematological disorders

### β-Haemoglobinopathies

Sickle cell anaemia was dubbed the first molecular disease in 1949 (ref. 136). Less than a decade later, the pathogenic amino acid substitution in sickle haemoglobin was identified as a gene mutation inherited in a strictly Mendelian manner137. Inherited mutations in the β-globin gene (HBB) lead to the most common inherited blood disorders worldwide, with approximately 60,000 and 300,000 annual diagnoses for TDT and SCD, respectively11,12,138. TDT mutations result in an imbalance between the α-globin and β-globin chains of adult haemoglobin, causing ineffective erythropoiesis12,138. The HBB-E6V SCD mutation results in the polymerization of deoxygenated sickle haemoglobin, causing erythrocyte deformation, haemolysis and vaso-occlusive episodes11,12. Matched sibling donor allogenic HSC transplantation (HSCT) offers a curative option with a >90% survival rate, although this approach is unavailable to most patients139,140. Alternative donor allogeneic transplantation remains an area of active clinical investigation141. Viral gene addition has also shown promising clinical efficacies, as reviewed elsewhere29, and provided a foundation for gene therapy of β-haemoglobinopathies. Challenges related to integrating viral vectors include the requirement of multiple vector copies per cell to achieve high-level expression, with some patients developing imbalanced globin expression142, which indicates that endogenous gene regulation would be preferred.

Restoring HbF expression offers a universal therapeutic strategy for all mutations causative of β-haemoglobin disorders, bypassing the need to develop personalized gene editing approaches for each of more than 350 pathogenic mutations138. Human genetics studies of rare and common variants associated with HbF level and with the clinical severity of TDT and SCD have helped pinpoint the genetic elements that silence HbF in adults, including the BCL11A erythroid enhancers and HBG1/2 promoters13,16,17,143,144,145. Disrupting the +58 or +55 erythroid-specific enhancers of BCL11A (ref. 16) via nuclease-driven indels or base editing has been shown to restore HbF expression and ameliorate disease phenotypes12,18,19,20,146,147,148 (Fig. 2a,b). Furthermore, naturally occurring mutations in the promoters of HBG1 and HBG2 have been linked to hereditary persistence of HbF (HPFH)149, and patients with SCD who express high levels of HbF present with much milder symptoms149. Therefore, another approach has involved installing HPFH or HPFH-like mutations at the HBG1 and HBG2 promoters via base editing, which generates binding sites for the activating transcription factors TAL1, GATA1 or KLF1 and/or disrupts the binding of repressors such as BCL11A or ZBTB7A (Fig. 2b). This approach also allows potent HbF induction to alleviate TDT and SCD103,150,151. Diverse approaches have also been developed to directly correct the SCD mutation using nuclease-driven HDR73,152, base editing102 and prime editing116,153 (Fig. 2b,c). Although the SCD HBB-E6V allele cannot be restored to wild type using base editing, custom adenine base editor variants recognizing non-canonical PAMs were used to convert the SCD allele into the non-pathogenic Makassar allele (HBB-E6A)65,102,154 (Fig. 2b). Finally, ex vivo and in vivo prime editing approaches were developed to restore the expression of WT β-globin116,153 (Fig. 2c). Although clinical hurdles were encountered using an HDR approach to directly correct the SCD allele76, these alternative base and prime editing strategies could overcome challenges related to the cell cycle dependence of HDR53 and the toxicity of the donor template77.

It can be anticipated that as novel therapies emerge with various delivery modalities (see below), patients with unique haematologic states will be described each containing varied mixtures of gene edit distributions across HSCs and haemoglobin distribution across erythroid cells. Future clinical research with detailed and long-term assessment of molecular, haematologic and clinical outcomes will be required to determine minimal therapeutic thresholds for overall and per-cell editing and haemoglobin distribution based on each editing approach. However, encouraging results have been observed in clinical studies of exa-cel, with average ~75% indels at the BCL11A enhancer and ~40% total HbF in patients with SCD, setting a point of comparison for future studies147. Together, significant progress has been made towards therapeutic gene editing for β-haemoglobinopathies, leading to the first FDA-approved CRISPR–Cas9 therapy (Box 1) and paving the way for other inherited blood disorders.

### Primary immunodeficiencies

Inborn errors of immunity are rare blood disorders characterized by defects in immune cell functions and susceptibility to severe infections. Among them, chronic granulomatous disease (CGD) is caused by defective function of the nicotinamide adenine dinucleotide phosphate (NADPH) oxidase complex responsible for phagocyte respiratory burst and superoxide production. Mutations in genes encoding components of the complex (such as the phox subunits) lead to inflammatory complications and recurrent invasive infections, the major cause of morbidity and mortality in patients with CGD155. HDR and ABE strategies have been developed to correct the prototypical X-linked chronic granulomatous disease (X-GCD) mutation in the CYBB gene (the R226X mutant of the p91phox subunit)104,156. In a side by side comparison, mice transplanted with ABE8e-SpRY-treated cells exhibited higher phenotypic correction compared with a nuclease-driven HDR method using an ssDNA donor104. Although this ABE approach relies on a near PAMless variant (SpRY)66, delivering the high-fidelity ABE8e-SpRY-HiFi variant as mRNA mitigated gRNA-dependent off-target editing events observed with ABE8e-SpRY. Together, these investigational new drug-enabling studies — including the profile of potential off-target DNA edits, transcriptome-wide RNA edits and chromosomal perturbations — provided support for initiating a first-in-human clinical trial for X-CGD using base editing (NCT06325709)104 (Table 1). Nuclease-driven HDR approaches have also been developed to correct the common delGT mutations in NCF1 (p47phox CGD), but frequently result in chromosomal deletions and rearrangements between NCF1 and its pseudogenes (NCF1B and NCF1C)157,158. Although p47phox CGD is not amenable to base editing, nucleotide insertion via prime editing offers a promising alternative. Indeed, the first-in-human clinical trial for prime editing (NCT06559176), sponsored by Prime Medicine, is designed to treat p47phox CGD (Table 1).

Among inborn errors of immunity amenable to diverse CRISPR-based technologies, severe congenital neutropenia is characterized by impaired neutrophil maturation, which leads to life-threatening infections in the absence of treatment. Mutations of the ELANE gene, encoding neutrophil elastase, account for around half of the cases of severe congenital neutropenia as well as the related condition cyclic neutropenia159. The only curative treatment for this blood disorder, allogeneic HSCT, is limited by donor availability and immune compatibility, with risks of graft-versus-host disease or graft rejection160. A leading model of pathogenicity suggests that abnormal neutrophil elastase proteins cause an unfolded protein response and endoplasmic reticulum stress, resulting in promyelocyte apoptosis and differentiation arrest at the promyelocyte-to-myelocyte transition161,162,163. We and others have previously dissected ELANE neutropenia pathogenicity and found that nuclease-driven indels triggering nonsense-mediated decay circumvent neutropenia mutations24,164. The promising target sequences identified offer a potential universal nuclease-based approach for therapeutic gene editing of all pathogenic ELANE mutations24,164 that could be portable to base and prime editing. Alternatively, inhibition of ELANE mRNA through the introduction of a staggered DSB initiated by two gRNAs targeting the promoter TATA box using SpCas9 nickase (D10A) also restored neutrophil maturation in patients’ HSPCs165.

Severe combined immunodeficiencies (SCIDs) are another group of disorders which cause profound lymphocytopenia and failure to thrive without treatment. Similar to β-haemoglobinopathies, the overall survival rate after HSCT from an HLA-matched sibling donor is greater than 90%, but is available for fewer than 20% of patients166,167,168. HSCT from alternative donors is associated with increased risks of graft-versus-host disease and incomplete immune reconstitution166,167,168. Gene therapies have been developed to provide a functional copy of a defective gene causing SCID. However, therapeutic transgene integration via gamma-retrovirus transduction has been linked with insertional oncogenesis169,170,171,172, although stem cell gene therapies for SCID have an improved safety profile with current-generation lentiviruses168,173. Nonetheless, in certain contexts, such as with the use of strong, viral-derived enhancer/promoter elements, lentiviral therapies can still be associated with insertional mutagenesis risk174,175. Recently, cases of haematologic cancer following gene therapy for cerebral adrenoleukodystrophy were reported in 7 out of 67 patients176. In six of these patients, expanded clones were found to contain at least one confirmed insertion site in the MECOM oncogene. Importantly, an internal MNDU3 promoter–enhancer included in the lentiviral vector to drive therapeutic-level expression of the deficient ABCD1 gene product might have contributed to insertional oncogenesis176. Extensive characterization of the mechanisms of clonal expansion and transformation is needed to better understand and mitigate these risks.

Targeted integration of a functional copy of a defective gene into its endogenous locus under physiological transcriptional control holds promise as an alternative to semi-random lentiviral integrations and could improve both the safety and the efficacy of gene correction177. This strategy has been used to functionally complement diverse SCID-causing genes, such as IL2RG (refs. 23,39,177), RAG1 (ref. 22) and RAG2 (refs. 178,179). These therapeutic avenues rely on HDR and could prove challenging to translate into the clinic76. On the other hand, developing personalized base or prime editing therapies for every pathogenic mutation causing SCID would require an immense amount of time and resources. Despite this barrier, developing gene therapies for orphan diseases remains important. McAuley et al. developed an ABE strategy to correct a CD3δ SCID mutation prevalent in rural Mennonite communities of North America, comprising more than 20% of SCID genotypes in Alberta, Canada25. As CRISPR-based gene therapies progress towards the clinic, developing personalized treatments to address unmet clinical needs for patients afflicted with very rare diseases should remain a priority and could benefit from a streamlined process.

### Bone marrow failure syndromes

Diverse defective cellular processes, including ribosomal biogenesis, DNA repair and telomere maintenance, have been linked with failure of the bone marrow to produce blood. Collectively known as inherited bone marrow failure syndromes, patients afflicted with these syndromes are at increased risk of developing blood cancers or life-threatening infections. Among these syndromes, Fanconi anaemia has been studied as a potential target for therapeutic genome editing. One fundamental obstacle lies in the mechanism of this disease. Normally implicated in DNA interstrand cross-link repair, the Fanconi anaemia DNA repair pathway is also needed for Cas9-induced single-strand template repair180. Although NHEJ-driven compensatory mutations could correct the phenotype in certain cases of Fanconi anaemia181, precise HDR gene correction using an ssDNA donor would be compromised in patient cells180. Alternatively, ABE has been used to functionally restore two prevalent mutant alleles of FANCA, which account for 60–65% of pathogenic FANCA mutations21. Of importance, base-edited HSPCs showed proliferative advantages21, corroborating previous findings of successful engraftment of gene-corrected HSCs in patients with Fanconi anaemia without a prior cytotoxic conditioning regimen182. Therapeutic genome editing of inherited bone marrow failure syndromes, where CRISPR-engineered HSCs would have a selective advantage over non-corrected cells, holds potential for the development of chemotherapy-free gene and cell therapies.

## Therapeutic challenges

### Genotoxic risks

Engineering the human genome poses potential safety risks. High levels of genotoxicity could lead to oligoclonal haematopoiesis and compromised graft resilience, potentially elevating the risk of haematologic cancer development. Evaluating and mitigating genotoxic risks associated with genome editing procedures, as well as optimizing protocols to achieve higher yields of gene-edited HSCs, are of paramount importance for ensuring the safety of CRISPR-based gene therapies for severe blood disorders. Long-term clonal tracking of gene-edited HSCs through the installation of synthetic barcodes183 and/or monitoring natural barcodes184 could also serve as a valuable tool to follow clonal composition and dynamics. Although progress has been made to evaluate and mitigate genotoxic risks, assays to determine the biological and clinical importance of any genomic effects are often lacking.

Multiple research groups have demonstrated that programmable RNA-guided genome editing tools can introduce undesired modifications at off-target loci (Fig. 3) and have developed unbiased detection methods for these modifications based on searching the genome in silico, in vitro or in cellulo185,186,187,188,189,190. Complementary approaches have also been developed to evaluate genome-wide and transcriptome-wide sgRNA-independent off-target activities of base editors89,90,91,92,93. One key consideration for clinical translation is human genetic diversity, as allele-specific off-targets can be concentrated in an ancestral group or be unique to an individual191. In the case of BCL11A enhancer editing, we found a genetic variant at CPS1 that creates a likely off-target site and is concentrated in individuals of African ancestry. It is expected to be carried by approximately 10% of patients with SCD191. Importantly, gene editing in HSPCs from a donor heterozygous for this off-target risk allele demonstrated that off-target indels and rearrangements were indeed produced, although they could be mitigated by using the HiFi Cas9 variant71,191. This finding prompted the FDA to mandate a post-marketing surveillance study for exa-cel, screen patients for the common CPS1 variant and test for allele-specific off-target editing in clinical samples. Although computational predictions allow variant-aware off-target nomination, novel methods are still needed to validate and mitigate off-target effects in cells of relevant genotypes192 as well as to determine their biological consequences, if any. Combining computational predictions of human genome off-target potential accounting for genetic diversity together with biological validations should facilitate the development of safer gene therapies.

Beyond off-target editing, additional genotoxic events include DSB-induced large deletions with extensive unidirectional end resection, and centromere-distal chromosome loss which can result in chromothripsis or the formation of micronuclei193,194,195,196 (Fig. 3). We recently found that these unintended outcomes are a by-product of cellular proliferation of HSPCs stimulated by ex vivo culture with cytokines55. Similarly, chromosome loss was mitigated in patient T cells when introducing Cas9-mediated DSBs prior to T cell activation/stimulation197. Micronuclei formation occurs in M phase198 whereas extensive end resection occurs in S/G2 phase53, suggesting that these genotoxic events are taking place in actively dividing cells. Increasing evidence indicates that HSCs, which are mostly quiescent in situ, possess unique DNA damage repair preferences compared with rapidly dividing progenitors18,39,73,75,199,200. Given that extended ex vivo culture with cytokines increases genotoxicity and negatively correlates with HSC engraftment potential201,202, targeting quiescent HSCs holds promise as an alternative to current clinical manufacturing protocols and could ultimately enable successful targeting of quiescent HSCs in situ.

Therapeutic gene editing using base or prime editors could mitigate DSB-induced genotoxic events. Nevertheless, using nickase-based systems decreases but does not completely abrogate large deletions and translocations94, which are more frequent with cytidine base editors due to suboptimal inhibition of BER, likely generating DSB intermediates. Concurrent SSBs generated via the PE3 system also generate staggered DSBs. PE3-mediated paired nicking generates 5′ or 3′ ssDNA overhang intermediates, leading to deletions or tandem duplications of the sequence between the cut sites, respectively, including in HSPCs108,117,203,204. Of importance, omitting the nick sgRNA (PE2 system) completely abrogated tandem duplications in HSPCs, and allowed highly efficient editing with high product purity with MMR-evading designs117. The PE3b system, where the nick sgRNA matches the edited strand and not the original allele9, minimizes the presence of concurrent nicks and offers a favourable compromise between efficiency and product purity in HSPCs when there is little flexibility for MMR evasion116,117. Considering the genome-wide specificity of prime editors9,205,206, these early preclinical results are encouraging for the goal of efficient therapeutic genome editing with minimal genotoxicity.

### Targeting quiescent HSCs

In their bone marrow niche, HSCs establish a state of metabolic and cell cycle dormancy known as functional quiescence207. Through their unique capability to self-renew and differentiate, HSCs ensure the lifelong production of all blood cells by delicately balancing pro-survival and stress-response mechanisms to restrain lineage commitment and support functional G0 phase cell cycle dormancy207,208. Pharmacological regulation of mTOR and Wnt signalling allows the ex vivo maintenance of LT-HSCs, suggesting a crucial role for these pathways in regulating stem cell renewal or lineage commitment208. Activation of the mTOR and JAK pathways drives HSCs from quiescence to rapid cycling, promoting lineage commitment and HSC depletion209,210,211. A recent study found that the c-Myc target MYCT1 limits environmental sensing to maintain HSC self-renewal and engraftment ability212. Interestingly, MYCT1 expression was markedly downregulated during ex vivo culture212. In therapeutic gene editing settings, mobilized peripheral blood CD34+ HSPCs are predominantly in G0 phase, and rapidly progress to G1 phase and then S/G2/M phase after 24 h and 48 h of ex vivo culture with cytokines, respectively18,55,74. Inducing quiescence by inhibiting mTORC1 and GSK-3 after editing and a short period of cycling improves HDR in LT-HSCs74. A chemically defined culture system has also been developed to support in vitro expansion of HSCs without conventional cytokines213. Overall, ex vivo cell culture and cytokine stimulation can present challenges to maintaining the engraftment and self-renewal potential of gene-modified HSCs.

The quiescent nature of HSCs also generates metabolic barriers for therapeutic gene editing. Ex vivo culture with cytokines drives HSCs from G0 to G1 phase18,55,74, inducing a reversible switch from metabolic dormancy to support the anabolic demands of cell division. This switch activates the translation machinery, allowing efficient genome editor expression via mRNA delivery. As HSCs are predominantly quiescent in their niche, it is not clear whether cytokine stimulation is needed for maximal base or prime editor mRNA expression, but this could potentially limit efficient base or prime editing in vivo using current mRNA modalities. Another key metabolic obstacle is the level of nucleotides that are available for reverse transcription, and thus prime editing. To support DNA replication and cell proliferation, the levels of dNTPs are orders of magnitude higher in actively dividing compared with quiescent cells214,215,216. SAMHD1, a triphosphohydrolase enzyme, tightly regulates the level of dNTPs in a cell cycle-dependent fashion and acts as an antiviral factor to restrict lentiviral infection in haematopoietic cells214,215,216. To counteract this defence mechanism, HIV-2 and SIV express the Vpx accessory protein, which associates with the CRL4-DCAF1 E3 ubiquitin ligase to target SAMHD1 for proteasomal degradation, thus raising dNTP levels to support viral infection. We demonstrated that modulating nucleotide metabolism by co-delivering Vpx mRNA and supplementing deoxynucleosides in the culture media enhance prime editing at the step of reverse transcription in HSPCs117. Altogether, future efforts at engineering HSCs in situ should consider the quiescent nature of HSCs and their metabolic constraints.

### Chemotherapy-free cell therapies

Autologous gene therapies, including exa-cel, typically rely on myeloablative conditioning to facilitate the engraftment of engineered HSPCs12,168,173. Although non-myeloablative chemotherapy can be sufficient for gene-corrected cells with a selective advantage to reach therapeutic levels, myeloablation is necessary for therapeutic indications dependent on high levels of engraftment, such as β-haemoglobinopathies and lysosomal storage disorders217. HSC gene therapies are therefore limited to the most severe forms of blood disorders, because genotoxic conditioning prior to transplantation is associated with acute toxicities such as cytopenias, mucositis, infection and organ injury (requiring inpatient support for 1–2 months), as well as long-term toxicities such as infertility, organ toxicity and risk of secondary malignancy134,166. In addition, stem cell collection can be onerous. Beam Therapeutics acknowledged the death of a patient due to respiratory failure 4 months after BEAM-101 infusion during a phase I/II clinical trial of base editing for SCD (NCT05456880)218 (Table 1). The complications were likely related to the myeloablative conditioning step using the DNA alkylating agent busulfan218. Also, the death of a patient with SCD was reported in the exa-cel trial, attributed to respiratory failure associated with coronavirus 2 (SARS-CoV-2) infection, along with busulfan-associated lung injury and pre-existing lung disease147.

Non-genotoxic conditioning regimens could improve the safety profile of autologous HSC-based therapies. Antibody–drug conjugates (ADCs) targeting antigens such as CD117/c-kit and CD45 expressed on HSCs might produce myeloablation and enable haematopoietic repopulation219,220,221,222. Studies in non-human primates have indeed shown that such ADCs allow for durable haematopoietic replacement by gene-modified HSCs223,224. A challenge is that no single antigen is expressed solely on HSCs — for example, CD117 is also expressed on mast cells, germ cells and various other non-haematopoietic cells, and CD45 on mature haematopoietic cells. A clinical trial testing an anti-CD117 ADC was paused following the death of a patient from cardiorespiratory failure225, suggesting that the clinical implementation of ADC-based myeloablative conditioning will require careful determination of safe and effective treatment regimens.

A promising alternative to toxic conditioning could be to mobilize existing HSPCs out of their niche while conferring a selective advantage to engineered cells, enabling efficient competitive engraftment. This paradigm has been exemplified by co-delivering mRNA to overexpress the homing receptor CXCR4 to repopulate bone marrow after prior mobilization treatment to produce niche space availability226. In addition, conferring selective advantage by multiplexed genome editing might help achieve therapeutic levels of editing without myeloablative conditioning. Targeting two endogenous loci with CRISPR–Cas9 results in double-editing events that are not statistically independent across a wide range of biological systems, including in Caenorhabditis elegans227, Drosophilia melanogaster228,229, and human cells108,230. Genome editing at a selectable endogenous gene enables the enrichment of a second genome modification of interest via marker-free co-selection, a process compatible with NHEJ, HDR, base editing and prime editing108,230. The mechanism of co-selection is not fully understood, but likely involves a combination of factors. Co-editing events might occur in cells that have the highest editor expression while being in a similar cell cycle stage and expressing the most favourable DNA repair factors. Additionally, other metabolic features might make some cells more amenable to completing multiple editing events at different loci. Building on this, strategies can be envisioned to improve the enrichment and engraftment of gene-corrected HSCs through CRISPR-driven introduction of selectable alleles. For example, epitope base editing of surface receptors in HSPCs confers resistance to monoclonal antibodies and chimeric antigen receptor (CAR) T cells, while maintaining receptor expression and function, and has enabled targeted immunotherapies for acute myeloid leukaemia, B cell lymphoma and T cell leukaemia231,232. Multiplexed epitope and therapeutic editing is a promising approach to engineer resistance to clinically used antibodies, which could be leveraged to enrich HSCs that harbour a therapeutic edit at a second locus of interest. Considering the progress made towards delivery of genome editors to HSCs in vivo233,234, marker-free co-selection strategies could facilitate gene therapy for severe blood disorders without ex vivo engineering and myeloablative conditioning.

## Improving broad patient access

The current model for the development of gene and cell therapies poses translational challenges for their broad accessibility to patients with severe blood disorders. This is especially true for rare genetic diseases that are not viable for pharmaceutical commercialization. For common blood disorders with a universal therapeutic strategy, such as the restoration of HbF expression for β-haemoglobinopathies, the main contemporary barriers are patient acceptance of therapies that, although potentially transformational, are still associated with substantial toxicity and complexity, the healthcare infrastructure needed to administer the autologous cell therapy, and the scientific and medical expertise needed to produce and administer gene therapies (Fig. 4). HSC mobilization, isolation and ex vivo manufacturing require extensive resources and scientific expertise. Additionally, administering the conditioning chemotherapy, transfusing engineered cells and monitoring the patient post transplantation necessitate at least 4–6 weeks of hospitalization (Fig. 4). Although potentially curative, the infrastructure and expertise needed to successfully provide the first CRISPR-based gene and cell therapies, as well as their cost235,236, will restrict their widespread administration. Navigating the complex intellectual properties involved in therapeutic genome editing also generates an additional layer of complexity. Considering that more than 300,000 babies are born every year with β-haemoglobinopathies, developing safe and efficient delivery methods to engineer HSCs in vivo could drastically improve broad patient accessibility.

### In vivo delivery

The development of drug delivery systems for CRISPR-based genome editors is making remarkable progress237, but engineering HSCs in vivo generates an additional layer of complexity. A suitable delivery system would safely and efficiently deliver the genome editor transiently to HSCs with minimal off-target cellular uptake, cytotoxicity and immunogenicity. To mitigate off-target effects, prolonged genome editor expression via integrating viral vector delivery might not be suitable for in vivo HSC engineering. In addition, vectors based on adenoviruses or AAVs can pose safety risks with regards to immunogenicity, dose-limiting toxicity, broad tropism, viral integration and unwanted long-term expression, and limited redosing capacity237,238,239,240,241,242,243. On the other hand, non-viral delivery systems offer promising alternatives to address these safety concerns.

The COVID-19 pandemic brought lipid nanoparticles (LNPs) (Fig. 5) and RNA therapeutics to the forefront of modern medicine. Pivotal discoveries, including the impact of mRNA nucleoside modification on the suppression of RNA recognition by Toll-like receptors244, enabled the development of life-saving mRNA vaccines245,246. LNPs are an up and coming modality for the transient delivery of genome editors. FDA-approved LNPs are composed of an ionizable lipid, a helper lipid, a polyethylene glycol (PEG) lipid and cholesterol (Fig. 5). The nanoscale structure of LNPs dictates their tropism, efficiency and safety, which motivated the development of a diverse suite of LNP chemistries to deliver genetic medicines237,247. Standard four-component LNPs leverage the physiological cholesterol transport of lipoproteins by binding to serum ApoE, followed by hepatocyte uptake through low-density lipoprotein receptor (LDL-R)-mediated endocytosis. To overcome liver accumulation, selective organ targeting LNPs have been developed via the addition of a defined amount of ionizable lipids, positively charged lipids or negatively charged lipids to increase the selective delivery of therapeutic mRNA to the liver, lungs and spleen, respectively248,249.

Different groups have demonstrated the portability of LNP-mediated mRNA delivery for HSC engineering ex vivo and in vivo233,234,250. The addition of covalent lipid species to 4-component LNPs created bone marrow-homing LNPs capable of transfecting 14 unique haematopoietic cell types, including HSCs234. Using a Townes (HBBs/s) mouse model of SCD, two bone marrow-homing LNP doses resulted in 2.4% base editing at HBB234. Interestingly, mass spectrometry proteomics identified ApoE as the top enriched serum protein that binds bone marrow-homing LNPs234. As quiescent HSCs do not express the ApoE-binding LDL-R251, LNP formulations depending on ApoE-mediated cellular uptake might be challenging for in vivo editing of LT-HSCs. Alternatively, anti-CD117-conjugated LNPs targeting the stem cell factor receptor enabled in vivo mRNA delivery to LT-HSCs233. Although promising, high levels of non-specific cellular uptake were observed in the liver and lungs after a single dose of CD117-LNPs233. Future research avenues could help LNPs reach therapeutic levels of editing while decreasing non-specific cellular uptake through formulation engineering, repeated dosing and stabilizing nucleic acid modifications. Among potential research directions, synthesis of therapeutic mRNA with altered topologies such as circularization252,253 or branched chemically modified poly(A) tails254 could improve genome editor mRNA stability when higher levels of expression are needed for efficient editing.

One of the main challenges in genome editor delivery is the endosomal release of the payload, also known as endosomal escape, which remains a highly recalcitrant problem with less than 5% release efficiency255,256. To complicate matters, the mechanism of endosomal escape is poorly understood256,257. Among the hypotheses, temporary, short-lived and small breaches in the endosomal lipid bilayer might allow RNA to reach the cytoplasm257. Some studies suggest that RNA payloads could leak out during endosome maturation as they move towards fusion with lysosomes255,257,258. Future efforts to improve endosomal escape by disrupting the lipid bilayer locally without rupturing the endosome (which causes cytotoxicity by releasing compartmentalized proteins and molecules into the cytoplasm) should facilitate therapeutic RNA delivery257. The development of alternative delivery strategies to overcome this barrier, and potentially bypass endosomes altogether — such as proteolipid vehicles259 or peptide-mediated RNP complex delivery260,261 — also merits further exploration. Indeed, highly efficient delivery and genome editing have been achieved ex vivo in primary T cells and HSPCs using a cell-penetrating Cas9 RNP and a cell-penetrating endosomal escape peptide260. Although efficient, further research is needed to evaluate the immunogenicity of peptide-mediated delivery systems.

Virus-like particles (VLPs) also hold potential to transiently deliver RNP complexes in vivo262,263,264,265,266,267,268 (Fig. 5). These assemblies of viral proteins carry a therapeutic RNP complex cargo instead of a viral genome and are pseudotyped with an envelope glycoprotein, allowing tissue-targeting without the risks of viral genome integration. To generate VLPs, MMLV Gag-pro-pol, Gag-linker-editor and VSV-G envelope glycoprotein vectors are co-transfected in a producer cell line to package the therapeutic RNP cargo (Fig. 5). The VLP platforms have enabled in vivo gene correction using base and prime editing267,268, but in vivo HSC engineering has yet to be achieved. Given that LDL-R serves as the cellular receptor for VSV-G269, current VLP modalities would not be suitable to target quiescent LT-HSCs in vivo251, but alternative envelope glycoproteins could potentially overcome this limitation270. Finally, antibody-targeted envelope delivery vehicles take advantage of a mutant VSV-G glycoprotein that maintains endosomal fusion activity while lacking native LDL-R binding affinity271 (Fig. 5). VLPs retargeted to primary T cells via CD3 and CD4 single-chain variable fragments (scFvs) allowed in vivo nuclease-driven editing, although at low efficiency271. Future improvements could redirect VLPs specifically to LT-HSCs, which lack the LDL-R needed for current LNPs and VLPs.

Altogether, efficient in vivo targeting of LT-HSCs will likely pose challenges for diverse inherited haematological disorders, especially β-haemoglobinopathies where high levels of editing are needed. Endowing CRISPR-engineered HSCs with a selective advantage might be necessary to enrich gene-corrected cells. Using the Townes SCD mouse model and adenoviral vector delivery, therapeutic levels of in vivo prime editing were only achieved through low-dose chemotherapy selection of transduced cells153. Coupling epitope editing231,232 with gene correction could bypass the need for toxic chemotherapy to achieve therapeutic levels of editing via marker-free co-selection108,230 using clinically relevant antibodies.

### Simplified manufacturing

The current manufacturing process for most autologous gene and cell therapies involves the collection of patient cells, which are then engineered off-site (Fig. 4). Rapid manufacturing protocols for lentiviral transduction of unstimulated primary T cells and HSPCs in 24 h or less have been developed272,273. Minimizing ex vivo manipulation could reduce costs and resources with the potential to decentralize cell therapy manufacturing to local host laboratories. Because unwanted events such as large deletions and centromere-distal chromosome fragment loss are by-products of cellular proliferation55,197, rapid cell engineering without ex vivo culture could both facilitate manufacturing and decrease genotoxicity. Considering these recent developments, ex vivo culture could be minimized in clinical settings to mitigate nuclease-driven genotoxicity. To further simplify cell therapy administration, the purification and engineering of CD34+ HSPCs could be performed in a closed system without culture prior to infusion, and even potentially at the bedside in a circuit in continuity with the patient.

## Summary and perspective

The translation of CRISPR–Cas9 from bacterial cultures for dairy products to the clinic was relatively rapid. In less than two decades, microbiologists discovered and characterized a diverse set of bacteriophage defence mechanisms while biomedical scientists repurposed and engineered CRISPR effector proteins to develop gene therapies for inherited genetic diseases. Building from rich clinical knowledge of allogeneic HSCT and conventional gene therapy, the first CRISPR–Cas9 therapy to cross the finish line, exa-cel, has provided hope for patients afflicted with inherited haematological disorders. Whereas exa-cel offers a compelling present-day therapeutic option, the development of more advanced and precise CRISPR-based technologies could further enhance the efficacy and safety profile of gene therapies for β-haemoglobinopathies. In addition, this landmark approval will undoubtedly set the stage for additional therapeutic indications. As the field moves forward, repurposing genome editing platforms to target new genes should streamline the expansion of CRISPR-based therapies to many more patients. FDA-approved therapies could be repurposed for new inherited disease indications by modifying the gRNA and validating the efficiency and specificity of the strategy. Benchmarking these next-generation gene therapies should reduce the time and resources needed to translate a genome editing strategy from the bench to the bedside.

Although promising, the development of a gene correction approach for every pathogenic mutation causative of severe blood disorders would require immense effort, at least until novel platform-based regulatory mechanisms are available. The restoration of HbF expression through nuclease-driven sequence disruption offers a universal approach to remedy hundreds of pathogenic mutations causative of β-haemoglobinopathies. Nevertheless, this paradigm is not applicable to most inherited genetic disorders. Targeted complementation of a defective gene with a functional copy under physiological transcriptional control at its endogenous locus could also remedy diverse pathogenic mutations using a single genome editing strategy. Considering the quiescent nature of HSCs and the difficulties in achieving efficient HDR, new technologies are needed to achieve efficient targeted integration of therapeutic DNA in non-dividing cells. One key barrier for these emerging technologies is the toxicity of the dsDNA donors, which triggers an inflammatory transcriptional programme through cytosolic cGAS–STING sensing134,135. In addition, a recent study found that an endogenous RNase, SLFN11, triggers innate immune responses upon recognition of intracellular ssDNA274, generating an additional delivery barrier. Overcoming these DNA repair and immunological barriers should facilitate therapeutic genome editing of HSCs.

New challenges are emerging as the field moves towards in vivo genome editing. In their niche, quiescent HSCs are in metabolic dormancy. We recently found that the low levels of nucleotides available for reverse transcription restrict prime editing in HSPCs117. Co-delivering Vpx as mRNA using LNPs, or as a structural protein using VLPs, targeted SAMHD1 for proteasomal degradation and increased the level of nucleotide available for prime editing. Alternatively, increasing the affinity of reverse transcriptase for dNTPs117,275 or using DNA polymerase systems276, such as click editing277, could facilitate in vivo HSC engineering. The metabolic dormancy of HSCs could also limit editor mRNA translation using LNP delivery, whereas engineering mRNA with stabilizing modifications could improve editor expression254,278,279. Considering the low levels of editing achieved in vivo with current modalities, endowing engineered HSCs with a selective advantage appears especially important. The development of marker-free co-selection strategies108,230 using novel conditioning agents could address this limitation, although attention should be paid to maintaining clonal diversity.

Once optimized, therapeutic genome editing platforms could be expanded to new indications by developing target-to-therapy pipelines. Different indications will require adaptation, and the restoration of disease phenotypes should be assessed rigorously using appropriate models. Interactions with regulatory agencies are confidential, and there is no universal developmental path for therapeutic genome editing IND submission. Establishing transparent blueprints for IND-enabling studies should facilitate preclinical development. Novel regulatory paradigms might be needed to facilitate the implementation of individualized therapies, tailored to a patient’s genotype and clinical situation. Ultimately, gene editing strategies should be optimized for maximum editing efficiency with minimal genotoxicity, using healthy or patient HSPCs. Complementary assays should be performed to assess off-target editing using computational predictions and experimental validations. Human genetic diversity should be considered when assessing off-target activity191, and population-specific off-targets should be incorporated into the validation pipeline. Larger unwanted events, such as large deletions, translocations and centromere-distal chromosome loss should also be quantified using complementary genotyping approaches. After on-target optimization, and thoroughly validating and mitigating genotoxicity, therapeutic strategies could move forward in the translational pipeline to expand existing platforms to new therapeutic indications. Monitoring patients and their blood cells longitudinally to observe molecular, cellular and physiological outcomes of genome editing can both maximize knowledge and preserve patient trust.

The landmark approval of exa-cel is just the beginning, with more CRISPR-based therapies on the horizon. Streamlining the development of CRISPR-based therapies using approved platforms, along with ensuring freedom to operate after patent expirations, should improve broad patient access in the long term. For more common genetic diseases, such as SCD with approximately 300,000 new cases annually, commercial sponsors and academic investigators are working to develop the next frontier of safe and efficient delivery methods to engineer HSCs in vivo. Academic-led initiatives also strive to address unmet clinical needs for patients afflicted with orphan genetic conditions, including ‘n = 1’ diseases. Achieving precise and safe gene correction to restore a diseased blood system with minimal healthcare infrastructure could be transformative.

## References

[1]: Barrangou, R. et al. CRISPR provides acquired resistance against viruses in prokaryotes. Science 315, 1709–1712 (2007).

[2]: Garneau, J. E. et al. The CRISPR/Cas bacterial immune system cleaves bacteriophage and plasmid DNA. Nature 468, 67–71 (2010).

[3]: Jinek, M. et al. A programmable dual-RNA-guided DNA endonuclease in adaptive bacterial immunity. Science 337, 816–822 (2012).

[4]: Labrie, S. J., Samson, J. E. & Moineau, S. Bacteriophage resistance mechanisms. Nat. Rev. Microbiol. 8, 317–327 (2010).

[5]: Cong, L. et al. Multiplex genome engineering using CRISPR/Cas systems. Science 339, 819–823 (2013).

[6]: Mali, P. et al. RNA-guided human genome engineering via Cas9. Science 339, 823–826 (2013).

[7]: Komor, A. C., Kim, Y. B., Packer, M. S., Zuris, J. A. & Liu, D. R. Programmable editing of a target base in genomic DNA without double-stranded DNA cleavage. Nature 533, 420–424 (2016).

[8]: Gaudelli, N. M. et al. Programmable base editing of A•T to G•C in genomic DNA without DNA cleavage. Nature 551, 464–471 (2017).

[9]: Anzalone, A. V. et al. Search-and-replace genome editing without double-strand breaks or donor DNA. Nature 576, 149–157 (2019).

[10]: Bauer, D. E. & Orkin, S. H. Hemoglobin switching’s surprise: the versatile transcription factor BCL11A is a master repressor of fetal hemoglobin. Curr. Opin. Genet. Dev. 33, 62–70 (2015).

[11]: Piel, F. B., Steinberg, M. H. & Reese, D. C. Sickle cell disease. N. Engl. J. Med. 376, 1561–1573 (2017).

[12]: Frangoul, H. et al. CRISPR–Cas9 gene editing for sickle cell disease and β-thalassemia. N. Engl. J. Med. 384, 252–260 (2021).

[13]: Lettre, G. et al. DNA polymorphisms at the BCL11A, HBS1L-MYB, and β-globin loci associate with fetal hemoglobin levels and pain crises in sickle cell disease. Proc. Natl Acad. Sci. USA 105, 11869–11874 (2008).

[14]: Sankaran, V. G. et al. Human fetal hemoglobin expression is regulated by the developmental stage-specific repressor BCL11A. Science 322, 1839–1842 (2008).

[15]: Xu, J. et al. Correction of sickle cell disease in adult mice by interference with fetal hemoglobin silencing. Science 334, 993–996 (2011).

[16]: Bauer, D. E. et al. An erythroid enhancer of BCL11A subject to genetic variation determines fetal hemoglobin level. Science 342, 253–258 (2013).

[17]: Uda, M. et al. Genome-wide association study shows BCL11A associated with persistent fetal hemoglobin and amelioration of the phenotype of β-thalassemia. Proc. Natl Acad. Sci. USA 105, 1620–1625 (2008).

[18]: Wu, Y. et al. Highly efficient therapeutic gene editing of human hematopoietic stem cells. Nat. Med. 25, 776–783 (2019).

[19]: Zeng, J. et al. Therapeutic base editing of human hematopoietic stem cells. Nat. Med. 26, 535–541 (2020).

[20]: Canver, M. C. et al. BCL11A enhancer dissection by Cas9-mediated in situ saturating mutagenesis. Nature 527, 192–197 (2015).

[21]: Siegner, S. M. et al. Adenine base editing efficiently restores the function of Fanconi anemia hematopoietic stem and progenitor cells. Nat. Commun. 13, 6900 (2022).

[22]: Castiello, M. C. et al. Exonic knockout and knockin gene editing in hematopoietic stem and progenitor cells rescues RAG1 immunodeficiency. Sci. Transl. Med. 16, eadh8162 (2024).

[23]: Pavel-Dinu, M. et al. Gene correction for SCID-X1 in long-term hematopoietic stem cells. Nat. Commun. 10, 1634 (2019).

[24]: Rao, S. et al. Dissecting ELANE neutropenia pathogenicity by human HSC gene editing. Cell Stem Cell 28, 833–845.e5 (2021).

[25]: McAuley, G. E. et al. Human T cell generation is restored in CD3δ severe combined immunodeficiency through adenine base editing. Cell 186, 1398–1416.e23 (2023).

[26]: Gomez-Ospina, N. et al. Human genome-edited hematopoietic stem cells phenotypically correct mucopolysaccharidosis type I. Nat. Commun. 10, 4045 (2019).

[27]: Xu, L. et al. CRISPR/Cas9-mediated CCR5 ablation in human hematopoietic stem/progenitor cells confers HIV-1 resistance in vivo. Mol. Ther. 25, 1782–1789 (2017).

[28]: Xu, L. et al. CRISPR-edited stem cells in a patient with HIV and acute lymphocytic leukemia. N. Engl. J. Med. 381, 1240–1247 (2019).

[29]: Cavazzana, M., Bushman, F. D., Miccio, A., André-Schmutz, I. & Six, E. Gene therapy targeting haematopoietic stem cells for inherited diseases: progress and challenges. Nat. Rev. Drug. Discov. 18, 447–462 (2019).

[30]: Tucci, F., Galimberti, S., Naldini, L., Valsecchi, M. G. & Aiuti, A. A systematic review and meta-analysis of gene therapy with hematopoietic stem and progenitor cells for monogenic disorders. Nat. Commun. 13, 1315 (2022).

[31]: Mukhametzyanova, L. et al. Activation of recombinases at specific DNA loci by zinc-finger domain insertions. Nat. Biotechnol. 42, 1844–1854 (2024).

[32]: Durrant, M. G. et al. Bridge RNAs direct modular and programmable recombination of target and donor DNA. Nature 630, 984–993 (2024).

[33]: Nuñez, J. K. et al. Genome-wide programmable transcriptional memory by CRISPR-based epigenome editing. Cell 184, 2503–2519 (2021).

[34]: Cappelluti, M. A. et al. Durable and efficient gene silencing in vivo by hit-and-run epigenome editing. Nature 627, 416–423 (2024).

[35]: Rouet, P., Smih, F. & Jasin, M. Introduction of double-strand breaks into the genome of mouse cells by expression of a rare-cutting endonuclease. Mol. Cell Biol. 14, 8096–8106 (1994).

[36]: Kim, Y. G., Cha, J. & Chandrasegaran, S. Hybrid restriction enzymes: zinc finger fusions to Fok I cleavage domain. Proc. Natl Acad. Sci. USA 93, 1156–1160 (1996).

[37]: Porteus, M. H. & Baltimore, D. Chimeric nucleases stimulate gene targeting in human cells. Science 300, 763 (2003).

[38]: Urnov, F. D. et al. Highly efficient endogenous human gene correction using designed zinc-finger nucleases. Nature 435, 646–651 (2005).

[39]: Genovese, P. et al. Targeted genome editing in human repopulating haematopoietic stem cells. Nature 510, 235–240 (2014).

[40]: Perez, E. E. et al. Establishment of HIV-1 resistance in CD4+ T cells by genome editing using zinc-finger nucleases. Nat. Biotechnol. 26, 808–816 (2008).

[41]: Tebas, P. et al. Gene editing of CCR5 in autologous CD4 T cells of persons infected with HIV. N. Engl. J. Med. 370, 901–910 (2014).

[42]: Boch, J. et al. Breaking the code of DNA binding specificity of TAL-type III effectors. Science 326, 1509–1512 (2009).

[43]: Moscou, M. J. & Bogdanove, A. J. A simple cipher governs DNA recognition by TAL effectors. Science 326, 1501 (2009).

[44]: Miller, J. C. et al. A TALE nuclease architecture for efficient genome editing. Nat. Biotechnol. 29, 143–150 (2011).

[45]: Makarova, K. S. et al. Evolutionary classification of CRISPR–Cas systems: a burst of class 2 and derived variants. Nat. Rev. Microbiol. 18, 67–83 (2020).

[46]: Makarova, K. S. et al. An updated evolutionary classification of CRISPR–Cas systems. Nat. Rev. Microbiol. 13, 722–736 (2015).

[47]: Koonin, E. V., Makarova, K. S. & Zhang, F. Diversity, classification and evolution of CRISPR–Cas systems. Curr. Opin. Microbiol. 37, 67–78 (2017).

[48]: Anders, C., Niewoehner, O., Duerst, A. & Jinek, M. Structural basis of PAM-dependent target DNA recognition by the Cas9 endonuclease. Nature 513, 569–573 (2014).

[49]: Ivanov, I. E. et al. Cas9 interrogates DNA in discrete steps modulated by mismatches and supercoiling. Proc. Natl Acad. Sci. USA 117, 5853–5860 (2020).

[50]: Zhu, X. et al. Cryo-EM structures reveal coordinated domain motions that govern DNA cleavage by Cas9. Nat. Struct. Mol. Biol. 26, 679–685 (2019).

[51]: Pacesa, M. et al. R-loop formation and conformational activation mechanisms of Cas9. Nature 609, 191–196 (2022).

[52]: Nambiar, T. S., Baudrier, L., Billon, P. & Ciccia, A. CRISPR-based genome editing through the lens of DNA repair. Mol. Cell 82, 348–388 (2022).

[53]: Hustedt, N. & Durocher, D. The control of DNA repair by the cell cycle. Nat. Cell Biol. 19, 1–9 (2017).

[54]: Mao, Z., Bozzella, M., Seluanov, A. & Gorbunova, V. Comparison of nonhomologous end joining and homologous recombination in human cells. DNA Repair. 7, 1765–1771 (2008).

[55]: Zeng, J. et al. Gene editing without ex vivo culture evades genotoxicity in human hematopoietic stem cells. Cell Stem Cell 32, 191–208 (2025).

[56]: Ran, F. A. et al. In vivo genome editing using Staphylococcus aureus Cas9. Nature 520, 186–191 (2015).

[57]: Nishimasu, H. et al. Crystal structure of Staphylococcus aureus Cas9. Cell 162, 1113–1126 (2015).

[58]: Agudelo, D. et al. Versatile and robust genome editing with Streptococcus thermophilus CRISPR1–Cas9. Genome Res. 30, 107–117 (2020).

[59]: Amrani, N. et al. NmeCas9 is an intrinsically high-fidelity genome editing platform. Genome Biol. 19, 214 (2018).

[60]: Zetsche, B. et al. Cpf1 is a single RNA-guided endonuclease of a class 2 CRISPR–Cas system. Cell 163, 759–771 (2015).

[61]: Charlesworth, C. T. et al. Identification of preexisting adaptive immunity to Cas9 proteins in humans. Nat. Med. 25, 249–254 (2019).

[62]: Kleinstiver, B. P. et al. Engineered CRISPR–Cas9 nucleases with altered PAM specificities. Nature 523, 481–485 (2015).

[63]: Hu, J. H. et al. Evolved Cas9 variants with broad PAM compatibility and high DNA specificity. Nature 556, 57–63 (2018).

[64]: Nishimasu, H. et al. Engineered CRISPR–Cas9 nuclease with expanded targeting space. Science 361, 1259–1262 (2018).

[65]: Miller, S. M. et al. Continuous evolution of SpCas9 variants compatible with non-G PAMs. Nat. Biotechnol. 38, 471–481 (2020).

[66]: Walton, R. T., Christie, K. A., Whittaker, M. N. & Kleinstiver, B. P. Unconstrained genome targeting with near-PAMless engineered CRISPR–Cas9 variants. Science 368, 290–296 (2020).

[67]: Levesque, S., Agudelo, D. & Doyon, Y. Rewired Cas9s with minimal sequence constraints. Trends Pharmacol. Sci. 41, 429–431 (2020).

[68]: Kleinstiver, B. P. et al. High-fidelity CRISPR–Cas9 nucleases with no detectable genome-wide off-target effects. Nature 529, 490–495 (2016).

[69]: Slaymaker, I. M. et al. Rationally engineered Cas9 nucleases with improved specificity. Science 351, 84–88 (2016).

[70]: Lee, J. K. et al. Directed evolution of CRISPR–Cas9 to increase its specificity. Nat. Commun. 9, 3048 (2018).

[71]: Vakulskas, C. A. et al. A high-fidelity Cas9 mutant delivered as a ribonucleoprotein complex enables efficient gene editing in human hematopoietic stem and progenitor cells. Nat. Med. 24, 1216–1224 (2018).

[72]: Dever, D. P. et al. CRISPR/Cas9 β-globin gene targeting in human haematopoietic stem cells. Nature 539, 384–389 (2016).

[73]: DeWitt, M. A. et al. Selection-free genome editing of the sickle mutation in human adult hematopoietic stem/progenitor cells. Sci. Transl. Med. 8, 360ra134 (2016).

[74]: Shin, J. J. et al. Controlled cycling and quiescence enables efficient HDR in engraftment-enriched adult hematopoietic stem and progenitor cells. Cell Rep. 32, 108093 (2020).

[75]: Hoban, M. D. et al. Correction of the sickle cell disease mutation in human hematopoietic stem/progenitor cells. Blood 125, 2597–2604 (2015).

[76]: Philippidis, A. Graphite bio pauses lead gene editing program in sickle cell disease. Hum. Gene Ther. 34, 90 (2023).

[77]: Ferrari, S. et al. Choice of template delivery mitigates the genotoxic risk and adverse impact of editing in human hematopoietic stem cells. Cell Stem Cell 29, 1428–1444.e9 (2022).

[78]: Hanlon, K. S. et al. High levels of AAV vector integration into CRISPR-induced DNA breaks. Nat. Commun. 10, 4439 (2019).

[79]: Suchy, F. P. et al. Genome engineering with Cas9 and AAV repair templates generates frequent concatemeric insertions of viral vectors. Nat. Biotechnol. https://doi.org/10.1038/s41587-024-02171-w (2024).

[80]: Shy, B. R. et al. High-yield genome engineering in primary cells using a hybrid ssDNA repair template and small-molecule cocktails. Nat. Biotechnol. 41, 521–531 (2023).

[81]: Xie, K. et al. Efficient non-viral immune cell engineering using circular single-stranded DNA-mediated genomic integration. Nat. Biotechnol. https://doi.org/10.1038/s41587-024-02504-9 (2024).

[82]: Chen, B. et al. Dynamic imaging of genomic loci in living human cells by an optimized CRISPR/Cas system. Cell 155, 1479–1491 (2013).

[83]: Gilbert, L. A. et al. CRISPR-mediated modular RNA-guided regulation of transcription in eukaryotes. Cell 154, 442–451 (2013).

[84]: Perez-pinera, P. et al. RNA-guided gene activation by CRISPR–Cas9-based transcription factors. Nat. Methods 10, 973–979 (2013).

[85]: Chavez, A. et al. Highly efficient Cas9-mediated transcriptional programming. Nat. Methods 12, 326–328 (2015).

[86]: Nishida, K. et al. Targeted nucleotide editing using hybrid prokaryotic and vertebrate adaptive immune systems. Science 353, aaf8729 (2016).

[87]: Jiang, F. et al. Structures of a CRISPR–Cas9 R-loop complex primed for DNA cleavage. Science 351, 867–871 (2016).

[88]: Anzalone, A. V., Koblan, L. W. & Liu, D. R. Genome editing with CRISPR–Cas nucleases, base editors, transposases and prime editors. Nat. Biotechnol. 38, 824–844 (2020).

[89]: Zuo, E. et al. Cytosine base editor generates substantial off-target single-nucleotide variants in mouse embryos. Science 364, 289–292 (2019).

[90]: Jin, S. et al. Cytosine, but not adenine, base editors induce genome-wide off-target mutations in rice. Science 364, 292–295 (2019).

[91]: Doman, J. L., Raguram, A., Newby, G. A. & Liu, D. R. Evaluation and minimization of Cas9-independent off-target DNA editing by cytosine base editors. Nat. Biotechnol. 38, 620–628 (2020).

[92]: Grünewald, J. et al. Transcriptome-wide off-target RNA editing induced by CRISPR-guided DNA base editors. Nature 569, 433–437 (2019).

[93]: Grünewald, J. et al. CRISPR DNA base editors with reduced RNA off-target and self-editing activities. Nat. Biotechnol. 37, 1041–1048 (2019).

[94]: Fiumara, M. et al. Genotoxic effects of base and prime editing in human hematopoietic stem cells. Nat. Biotechnol. 42, 877–891 (2024).

[95]: Komor, A. C. et al. Improved base excision repair inhibition and bacteriophage Mu Gam protein yields C:G-to-T:A base editors with higher efficiency and product purity. Sci. Adv. 3, eaao4774 (2017).

[96]: Koblan, L. W. et al. Improving cytidine and adenine base editors by expression optimization and ancestral reconstruction. Nat. Biotechnol. 36, 843–848 (2018).

[97]: Richter, M. F. et al. Phage-assisted evolution of an adenine base editor with improved Cas domain compatibility and activity. Nat. Biotechnol. 38, 883–891 (2020).

[98]: Gaudelli, N. M. et al. Directed evolution of adenine base editors with increased activity and therapeutic application. Nat. Biotechnol. 38, 892–900 (2020).

[99]: Neugebauer, M. E. et al. Evolution of an adenine base editor into a small, efficient cytosine base editor with low off-target activity. Nat. Biotechnol. 41, 673–685 (2022).

[100]: Chen, L. et al. Re-engineering the adenine deaminase TadA-8e for efficient and specific CRISPR-based cytosine base editing. Nat. Biotechnol. 41, 663–672 (2023).

[101]: Lam, D. K. et al. Improved cytosine base editors generated from TadA variants. Nat. Biotechnol. 41, 686–697 (2023).

[102]: Newby, G. A. et al. Base editing of haematopoietic stem cells rescues sickle cell disease in mice. Nature 595, 295–302 (2021).

[103]: Mayuranathan, T. et al. Potent and uniform fetal hemoglobin induction via base editing. Nat. Genet. 55, 1210–1220 (2023).

[104]: Bzhilyanskaya, V. et al. High-fidelity PAMless base editing of hematopoietic stem cells to treat chronic granulomatous disease. Sci. Transl. Med. 16, eadj6779 (2024).

[105]: Luan, D. D. & Eickbush, T. H. RNA template requirements for target DNA-primed reverse transcription by the R2 retrotransposable element. Mol. Cell Biol. 15, 3882–3891 (1995).

[106]: Chen, P. J. et al. Enhanced prime editing systems by manipulating cellular determinants of editing outcomes. Cell 184, 5635–5652 (2021).

[107]: Ferreira da Silva, J. et al. Prime editing efficiency and fidelity are enhanced in the absence of mismatch repair. Nat. Commun. 13, 760 (2022).

[108]: Levesque, S. et al. Marker-free co-selection for successive rounds of prime editing in human cells. Nat. Commun. 13, 5909 (2022).

[109]: Tao, J., Wang, Q., Mendez-Dorantes, C., Burns, K. H. & Chiarle, R. Frequency and mechanisms of LINE-1 retrotransposon insertions at CRISPR/Cas9 sites. Nat. Commun. 13, 3685 (2022).

[110]: Warren, J. J. et al. Structure of the human MutSα DNA lesion recognition complex. Mol. Cell 26, 579–592 (2007).

[111]: Gupta, S., Gellert, M. & Yang, W. Mechanism of mismatch recognition revealed by human MutSβ bound to unpaired DNA loops. Nat. Struct. Mol. Biol. 19, 72–79 (2012).

[112]: Pluciennik, A. et al. PCNA function in the activation and strand direction of MutLα endonuclease in mismatch repair. Proc. Natl Acad. Sci. USA 107, 16066–16071 (2010).

[113]: Genschel, J., Bazemore, L. R. & Modrich, P. Human exonuclease I is required for 5′ and 3′ mismatch repair. J. Biol. Chem. 277, 13302–13311 (2002).

[114]: Longley, M. J., Pierce, A. J. & Modrich, P. DNA polymerase δ is required for human mismatch repair in vitro. J. Biol. Chem. 272, 10917–10921 (1997).

[115]: Zhang, Y. et al. Reconstitution of 5′-directed human mismatch repair in a purified system. Cell 122, 693–705 (2005).

[116]: Everette, K. A. et al. Ex vivo prime editing of patient haematopoietic stem cells rescues sickle-cell disease phenotypes after engraftment in mice. Nat. Biomed. Eng. 7, 616–628 (2023).

[117]: Levesque, S., Cosentino, A., Verma, A., Genovese, P. & Bauer, D. E. Enhancing prime editing in hematopoietic stem and progenitor cells by modulating nucleotide metabolism. Nat. Biotechnol. 43, 534–538 (2025).

[118]: Kim-yip, R. P. et al. Efficient prime editing in two-cell mouse embryos using PEmbryo. Nat. Biotechnol. 42, 1822–1830 (2023).

[119]: Li, X. et al. Highly efficient prime editing by introducing same-sense mutations in pegRNA or stabilizing its structure. Nat. Commun. 13, 1669 (2022).

[120]: Su, S. S., Lahue, R. S., Au, K. G. & Modrich, P. Mispair specificity of methyl-directed DNA mismatch correction in vitro. J. Biol. Chem. 263, 6829–6835 (1988).

[121]: Thomas, D. C., Roberts, J. D. & Kunkel, T. A. Heteroduplex repair in extracts of human HeLa cells. J. Biol. Chem. 266, 3744–3751 (1991).

[122]: Lahue, R., Au, K. & Modrich, P. DNA mismatch correction in a defined system. Science 245, 160–164 (1998).

[123]: Yan, J. et al. Improving prime editing with an endogenous small RNA-binding protein. Nature 628, 639–647 (2024).

[124]: Nelson, J. W. et al. Engineered pegRNAs improve prime editing efficiency. Nat. Biotechnol. 40, 402–410 (2021).

[125]: Anzalone, A. V. et al. Programmable deletion, replacement, integration and inversion of large DNA sequences with twin prime editing. Nat. Biotechnol. 40, 731–740 (2022).

[126]: Wang, J. et al. Efficient targeted insertion of large DNA fragments without DNA donors. Nat. Methods 19, 331–340 (2022).

[127]: Jiang, T., Zhang, X., Weng, Z. & Xue, W. Deletion and replacement of long genomic sequences using prime editing. Nat. Biotechnol. 40, 227–234 (2021).

[128]: Chen, P. J. & Liu, D. R. Prime editing for precise and highly versatile genome manipulation. Nat. Rev. Genet. 24, 161–177 (2022).

[129]: Choi, J. et al. Precise genomic deletions using paired prime editing. Nat. Biotechnol. 40, 218–226 (2022).

[130]: Pandey, S. et al. Efficient site-specific integration of large genes in mammalian cells via continuously evolved recombinases and prime editing. Nat. Biomed. Eng. 9, 22–39 (2025).

[131]: Yarnall, M. T. N. et al. Drag-and-drop genome insertion of large sequences without double-strand DNA cleavage using CRISPR-directed integrases. Nat. Biotechnol. 41, 500–512 (2022).

[132]: Hew, B. E. et al. Directed evolution of hyperactive integrases for site specific insertion of transgenes. Nucleic Acids Res. 52, e64 (2024).

[133]: Lampe, G. D. et al. Targeted DNA integration in human cells without double-strand breaks using CRISPR-associated transposases. Nat. Biotechnol. 42, 87–98 (2024).

[134]: Charlesworth, C. T., Hsu, I., Wilkinson, A. C. & Nakauchi, H. Immunological barriers to haematopoietic stem cell gene therapy. Nat. Rev. Immunol. 22, 719–733 (2022).

[135]: Decout, A., Katz, J. D., Venkatraman, S. & Ablasser, A. The cGAS–STING pathway as a therapeutic target in inflammatory diseases. Nat. Rev. Immunol. 21, 548–569 (2021).

[136]: Pauling, L., Itano, H. A., Singer, S. & Wells, I. C. Sickle cell anemia, a molecular disease. Science 110, 543–548 (1949).

[137]: Ingram, V. M. Gene mutations in human haemoglobin: the chemical difference between normal and sickle cell haemoglobin. Nature 180, 326–328 (1957).

[138]: Taher, A. T., Musallam, K. M. & Cappellini, D. M. β-Thalassemias. N. Engl. J. Med. 384, 727–743 (2021).

[139]: Zaidman, I., Rowe, J. M., Khalil, A., Ben-Arush, M. & Elhasid, R. Allogeneic stem cell transplantation in congenital hemoglobinopathies using a tailored busulfan-based conditioning regimen: single-center experience. Biol. Blood Marrow Transplant. 22, 1043–1048 (2016).

[140]: Srivastava, A. & Shaji, R. V. Cure for thalassemia major—from allogeneic hematopoietic stem cell transplantation to gene therapy. Haematologica 102, 214–223 (2017).

[141]: Inam, Z., Tisdale, J. F. & Leonard, A. Outcomes and long-term effects of hematopoietic stem cell transplant in sickle cell disease. Expert. Rev. Hematol. 16, 879–903 (2023).

[142]: Walters, M. C. et al. Lovo-cel (bb1111) gene therapy for sickle cell disease: updated clinical results and investigations into two cases of anemia from group C of the phase 1/2 HGB-206 study. Blood 140, 26–28 (2022).

[143]: Forget, B. G. Molecular basis of hereditary persistence of fetal hemoglobin. Ann. N. Y. Acad. Sci. 850, 38–44 (1998).

[144]: Menzel, S. et al. A QTL influencing F cell production maps to a gene encoding a zinc-finger protein on chromosome 2p15. Nat. Genet. 39, 1197–1199 (2007).

[145]: Traxler, E. A. et al. A genome-editing strategy to treat β-hemoglobinopathies that recapitulates a mutation associated with a benign genetic condition. Nat. Med. 22, 987–990 (2016).

[146]: Locatelli, F. et al. Exagamglogene autotemcel for transfusion-dependent β-thalassemia. N. Engl. J. Med. 390, 1663–1676 (2024).

[147]: Frangoul, H. et al. Exagamglogene autotemcel for severe sickle cell disease. N. Engl. J. Med. 390, 1649–1662 (2024).

[148]: Fu, B. et al. CRISPR–Cas9-mediated gene editing of the BCL11A enhancer for pediatric β0/β0 transfusion-dependent β-thalassemia. Nat. Med. 28, 1573–1580 (2022).

[149]: Wienert, B., Martyn, G. E., Funnell, A. P. W., Quinlan, K. G. R. & Crossley, M. Wake-up sleepy gene: reactivating fetal globin for β-hemoglobinopathies. Trends Genet. 34, 927–940 (2018).

[150]: Ravi, N. S. et al. Identification of novel HPFH-like mutations by CRISPR base editing that elevate the expression of fetal hemoglobin. eLife 11, e65421 (2022).

[151]: Antoniou, P. et al. Base-editing-mediated dissection of a γ-globin cis-regulatory element for the therapeutic reactivation of fetal hemoglobin expression. Nat. Commun. 13, 6618 (2022).

[152]: Lattanzi, A. et al. Development of β-globin gene correction in human hematopoietic stem cells as a potential durable treatment for sickle cell disease. Sci. Transl. Med 13, eabf2444 (2021).

[153]: Li, C. et al. In vivo HSC prime editing rescues sickle cell disease in a mouse model. Blood 141, 2085–2099 (2023).

[154]: Chu, S. H. et al. Rationally designed base editors for precise editing of the sickle cell disease mutation. CRISPR J. 4, 169–177 (2021).

[155]: Marciano, B. E. et al. Common severe infections in chronic granulomatous disease. Clin. Infect. Dis. 60, 1176–1183 (2015).

[156]: De Ravin, S. S. et al. CRISPR–Cas9 gene repair of hematopoietic stem cells from patients with X-linked chronic granulomatous disease. Sci. Transl. Med. 9, eaah3480 (2017).

[157]: Wrona, D. et al. CRISPR-directed therapeutic correction at the NCF1 locus is challenged by frequent incidence of chromosomal deletions. Mol. Ther. Methods Clin. Dev. 17, 936–943 (2020).

[158]: Raimondi, F. et al. Gene editing of NCF1 loci is associated with homologous recombination and chromosomal rearrangements. Commun. Biol. 7, 1291 (2024).

[159]: Köllner, I. et al. Mutations in neutrophil elastase causing congenital neutropenia lead to cytoplasmic protein accumulation and induction of the unfolded protein response. Blood 108, 493–500 (2006).

[160]: Connelly, J. A., Choi, S. W. & Levine, J. E. Hematopoietic stem cell transplantation for severe congenital neutropenia. Curr. Opin. Hematol. 19, 44–51 (2012).

[161]: Nayak, R. C. et al. Pathogenesis of ELANE-mutant severe neutropenia revealed by induced pluripotent stem cells. J. Clin. Investig. 125, 3103–3116 (2015).

[162]: Horwitz, M. S. et al. Neutrophil elastase in cyclic and severe congenital neutropenia. Blood 109, 1817–1824 (2007).

[163]: Grenda, D. S. et al. Mutations of the ELA2 gene found in patients with severe congenital neutropenia induce the unfolded protein response and cellular apoptosis. Blood 110, 4179–4187 (2007).

[164]: Nasri, M. et al. CRISPR/Cas9-mediated ELANE knockout enables neutrophilic maturation of primary hematopoietic stem and progenitor cells and induced pluripotent stem cells of severe congenital neutropenia patients. Haematologica 105, 598–609 (2020).

[165]: Nasri, M. et al. CRISPR–Cas9n-mediated ELANE promoter editing for gene therapy of severe congenital neutropenia. Mol. Ther. 32, 1628–1642 (2024).

[166]: Cowan, M. J., Neven, B., Cavazanna-Calvo, M., Fischer, A. & Puck, J. Hematopoietic stem cell transplantation for severe combined immunodeficiency diseases. Biol. Blood Marrow Transplant. 14, 73–80 (2008).

[167]: Neven, B. et al. Long-term outcome after hematopoietic stem cell transplantation of a single-center cohort of 90 patients with severe combined immunodeficiency. Blood 113, 4114–4124 (2009).

[168]: Mamcarz, E. et al. Lentiviral gene therapy combined with low-dose busulfan in infants with SCID-X1. N. Engl. J. Med. 380, 1525–1534 (2019).

[169]: Woods, N.-B., Bottero, V., Schmidt, M., Von Kalle, C. & Verma, I. M. Therapeutic gene causing lymphoma. Nature 440, 1123 (2006).

[170]: Hacein-Bey-Abina, S. et al. Insertional oncogenesis in 4 patients after retrovirus-mediated gene therapy of SCID-X1. J. Clin. Invest. 118, 3132–3142 (2008).

[171]: Von Kalle, C., Deichmann, A. & Schmidt, M. Vector integration and tumorigenesis. Hum. Gene Ther. 25, 475–481 (2014).

[172]: Hacein-Bey-Abina, S. et al. LMO2-associated clonal T cell proliferation in two patients after gene therapy for SCID-XI. Science 302, 415–419 (2003).

[173]: Kohn, D. B. et al. Autologous ex vivo lentiviral gene therapy for adenosine deaminase deficiency. N. Engl. J. Med. 384, 2002–2013 (2021).

[174]: Montini, E. et al. The genotoxic potential of retroviral vectors is strongly modulated by vector design and integration site selection in a mouse model of HSC gene therapy. J. Clin. Investig. 119, 964–975 (2009).

[175]: Williams, D. A. The long road traveled in hematopoietic stem cell gene therapy. Mol. Ther. 30, 3097–3099 (2022).

[176]: Duncan, C. N. et al. Hematologic cancer after gene therapy for cerebral adrenoleukodystrophy. N. Engl. J. Med. 391, 1287–1301 (2024).

[177]: Brault, J. et al. CRISPR–Cas9–AAV versus lentivector transduction for genome modification of X-linked severe combined immunodeficiency hematopoietic stem cells. Front. Immunol. 13, 1067417 (2023).

[178]: Allen, D. et al. CRISPR–Cas9 engineering of the RAG2 locus via complete coding sequence replacement for therapeutic applications. Nat. Commun. 14, 6771 (2023).

[179]: Pavel-Dinu, M. et al. Genetically corrected RAG2-SCID human hematopoietic stem cells restore V(D)J-recombinase and rescue lymphoid deficiency. Blood Adv. 8, 1820–1833 (2024).

[180]: Richardson, C. D. et al. CRISPR–Cas9 genome editing in human cells works via the Fanconi anemia pathway. Nat. Genet. 50, 1132–1139 (2018).

[181]: Román-Rodríguez, F. J. et al. NHEJ-mediated repair of CRISPR–Cas9-induced DNA breaks efficiently corrects mutations in HSPCs from patients with Fanconi anemia. Cell Stem Cell 25, 607–621 (2019).

[182]: Río, P. et al. Successful engraftment of gene-corrected hematopoietic stem cells in non-conditioned patients with Fanconi anemia. Nat. Med. 25, 1396–1401 (2019).

[183]: Ferrari, S. et al. Efficient gene editing of human long-term hematopoietic stem cells validated by clonal tracking. Nat. Biotechnol. 38, 1298–1308 (2020).

[184]: Lee-Six, H. et al. Population dynamics of normal human blood inferred from somatic mutations. Nature 561, 473–478 (2018).

[185]: Tsai, S. Q. et al. GUIDE-seq enables genome-wide profiling of off-target cleavage by CRISPR–Cas nucleases. Nat. Biotechnol. 33, 187–198 (2015).

[186]: Wienert, B. et al. Unbiased detection of CRISPR off-targets in vivo using DISCOVER-Seq. Science 364, 286–289 (2019).

[187]: Lazzarotto, C. R. et al. CHANGE-seq reveals genetic and epigenetic effects on CRISPR–Cas9 genome-wide activity. Nat. Biotechnol. 38, 1317–1327 (2020).

[188]: Turchiano, G. et al. Quantitative evaluation of chromosomal rearrangements in gene-edited human stem cells by CAST-Seq. Cell Stem Cell 28, 1136–1147.e5 (2021).

[189]: Kim, D. et al. Digenome-seq: genome-wide profiling of CRISPR–Cas9 off-target effects in human cells. Nat. Methods 12, 237–243 (2015).

[190]: Cameron, P. et al. Mapping the genomic landscape of CRISPR–Cas9 cleavage. Nat. Methods 14, 600–606 (2017).

[191]: Cancellieri, S. et al. Human genetic diversity alters therapeutic gene editing off-target outcomes. Nat. Genet. 55, 34–43 (2023).

[192]: Lin, J. et al. Scalable assessment of genome editing off-targets associated with genetic variants. Preprint at bioRxiv https://www.biorxiv.org/content/10.110 (2024).

[193]: Kosicki, M. & Bradley, A. Repair of CRISPR–Cas9-induced double-stranded breaks leads to large deletions and complex rearrangements. Nat. Biotechnol. 36, 765–771 (2018).

[194]: Leibowitz, M. et al. Chromothripsis as an on-target consequence of CRISPR–Cas9 genome editing. Nat. Genet. 53, 895–905 (2021).

[195]: Nahmad, A. D. et al. Frequent aneuploidy in primary human T cells following CRISPR–Cas9 cleavage. Nat. Biotechnol. 40, 1807–1813 (2022).

[196]: Park, S. H. et al. Comprehensive analysis and accurate quantification of unintended large gene modifications induced by CRISPR–Cas9 gene editing. Sci. Adv. 8, eabo7676 (2022).

[197]: Tsuchida, C. A. et al. Mitigation of chromosome loss in clinical CRISPR–Cas9-engineered T cells. Cell 186, 4567–4582.e20 (2023).

[198]: Liu, S. & Pellman, D. The coordination of nuclear envelope assembly and chromosome segregation in metazoans. Nucleus 11, 35–52 (2020).

[199]: Maganti, H. B. et al. Persistence of CRISPR/Cas9 gene edited hematopoietic stem cells following transplantation: a systematic review and meta-analysis of preclinical studies. Stem Cell Transl. Med. 10, 996–1007 (2021).

[200]: Mohrin, M. et al. Hematopoietic stem cell quiescence promotes error-prone DNA repair and mutagenesis. Cell Stem Cell 7, 174–185 (2010).

[201]: Lauridsen, F. K. B. et al. Differences in cell cycle status underlie transcriptional heterogeneity in the HSC compartment. Cell Rep. 24, 766–780 (2018).

[202]: Oedekoven, C. A. et al. Hematopoietic stem cells retain functional potential and molecular identity in hibernation cultures. Stem Cell Rep. 16, 1614–1628 (2021).

[203]: Bothmer, A. et al. Characterization of the interplay between DNA repair and CRISPR/Cas9-induced DNA lesions at an endogenous locus. Nat. Commun. 8, 13905 (2017).

[204]: Schimmel, J., Muñoz-Subirana, N., Kool, H., van Schendel, R. & Tijsterman, M. Small tandem DNA duplications result from CST-guided Pol α-primase action at DNA break termini. Nat. Commun. 12, 4843 (2021).

[205]: Kim, D. Y., Moon, S. B., Ko, J. H., Kim, Y. S. & Kim, D. Unbiased investigation of specificities of prime editing systems in human cells. Nucleic Acids Res. 48, 10576–10589 (2020).

[206]: Liang, S. et al. Genome-wide profiling of prime editor off-target sites in vitro and in vivo using PE-tag. Nat. Methods 20, 898–907 (2023).

[207]: Kasbekar, M., Mitchell, C. A., Proven, M. A. & Passegué, E. Hematopoietic stem cells through the ages: a lifetime of adaptation to organismal demands. Cell Stem Cell 30, 1403–1420 (2023).

[208]: Huang, J., Nguyen-Mccarty, M., Hexner, E. O., Danet-Desnoyers, G. & Klein, P. S. Maintenance of hematopoietic stem cells through regulation of Wnt and mTOR pathways. Nat. Med. 18, 1778–1785 (2012).

[209]: Chen, C. et al. TSC-mTOR maintains quiescence and function of hematopoietic stem cells by repressing mitochondrial biogenesis and reactive oxygen species. J. Exp. Med. 205, 2397–2408 (2008).

[210]: Ito, K. & Suda, T. Metabolic requirements for the maintenance of self-renewing stem cells. Nat. Rev. Mol. Cell Biol. 15, 243–256 (2014).

[211]: Johnson, C. S. et al. Adaptation to ex vivo culture reduces human hematopoietic stem cell activity independently of the cell cycle. Blood 144, 729–741 (2024).

[212]: Aguadé-Gorgorió, J. et al. MYCT1 controls environmental sensing in human haematopoietic stem cells. Nature 630, 412–420 (2024).

[213]: Sakurai, M. et al. Chemically defined cytokine-free expansion of human haematopoietic stem cells. Nature 615, 127–133 (2023).

[214]: Ayinde, D., Casartelli, N. & Schwartz, O. Restricting HIV the SAMHD1 way: through nucleotide starvation. Nat. Rev. Microbiol. 10, 675–680 (2012).

[215]: Ballana, E. & Esté, J. A. SAMHD1: at the crossroads of cell proliferation, immune responses, and virus restriction. Trends Microbiol. 23, 680–692 (2015).

[216]: Mauney, C. H. & Hollis, T. SAMHD1: recurring roles in cell cycle, viral restriction, cancer, and innate immunity. Autoimmunity 51, 96–110 (2018).

[217]: Bernardo, M. E. & Aiuti, A. The role of conditioning in hematopoietic stem-cell gene therapy. Hum. Gene Ther. 27, 741–748 (2016).

[218]: Philippidis, A. Patient dies in beam trial of sickle cell disease candidate; company cites conditioning. Hum. Gene Ther. 35, 951–954 (2024).

[219]: Palchaudhuri, R. et al. Non-genotoxic conditioning for hematopoietic stem cell transplantation using a hematopoietic-cell-specific internalizing immunotoxin. Nat. Biotechnol. 34, 738–745 (2016).

[220]: Czechowicz, A., Kraft, D., Weissman, I. L. & Bhattacharya, D. Efficient transplantation via antibody-based clearance of hematopoietic stem cell niches. Science 318, 1296–1299 (2007).

[221]: Kown, H.-S. et al. Anti-human CD117 antibody-mediated bone marrow niche clearance in nonhuman primates and humanized NSG mice. Blood 133, 2104–2108 (2019).

[222]: Czechowicz, A. et al. Selective hematopoietic stem cell ablation using CD117-antibody–drug-conjugates enables safe and effective transplantation with immunity preservation. Nat. Commun. 10, 617 (2019).

[223]: Uchida, N. et al. Fertility-preserving myeloablative conditioning using single-dose CD117 antibody–drug conjugate in a rhesus gene therapy model. Nat. Commun. 14, 6291 (2023).

[224]: Demirci, S. et al. BCL11A +58/+55 enhancer-editing facilitates HSPC engraftment and HbF induction in rhesus macaques conditioned with a CD45 antibody–drug conjugate. Cell Stem Cell 32, 209–226 (2025).

[225]: US National Library of Medicine. ClinicalTrials.gov https://clinicaltrials.gov/study/NCT05223699 (2023).

[226]: Omer-Javed, A. et al. Mobilization-based chemotherapy-free engraftment of gene-edited human hematopoietic stem cells. Cell 185, 2248–2264.e21 (2022).

[227]: Kim, H. et al. A Co-CRISPR strategy for efficient genome editing in Caenorhabditis elegans. Genetics 197, 1069–1080 (2014).

[228]: Kane, N. S., Vora, M., Varre, K. J. & Padgett, R. W. Efficient screening of CRISPR/Cas9-induced events in Drosophila using a Co-CRISPR strategy. G3 7, 87–93 (2017).

[229]: Tianfang Ge, D., Tipping, C., Brodsky, M. H. & Zamore, P. D. Rapid screening for CRISPR-directed editing of the Drosophila genome using white coconversion. G3 6, 3197–3206 (2016).

[230]: Agudelo, D. et al. Marker-free coselection for CRISPR-driven genome editing in human cells. Nat. Methods 14, 615–620 (2017).

[231]: Casirati, G. et al. Epitope editing enables targeted immunotherapies for acute myeloid leukemia. Nature 621, 404–414 (2023).

[232]: Wellhausen, N. et al. Epitope base editing CD45 in hematopoietic cells enables universal blood cancer immune therapy. Sci. Transl. Med. 15, eadi1145 (2023).

[233]: Breda, L. et al. In vivo hematopoietic stem cell modification by mRNA delivery. Science 381, 436–443 (2023).

[234]: Lian, X. et al. Bone-marrow-homing lipid nanoparticles for genome editing in diseased and malignant haematopoietic stem cells. Nat. Nanotechnol. 19, 1409–1417 (2024).

[235]: Sheridan, C. The world’s first CRISPR therapy is approved: who will receive it? Nat. Biotechnol. 42, 3–4 (2024).

[236]: Mullard, A. CRISPR gets the glory in landmark approval, but haemoglobin research made it possible. Nat. Rev. Drug. Discov. 23, 14–15 (2024).

[237]: Madigan, V., Zhang, F. & Dahlman, J. E. Drug delivery systems for CRISPR-based genome editors. Nat. Rev. Drug. Discov. 22, 875–894 (2023).

[238]: Lozier, J. N., Metzger, M. E., Donahue, R. E. & Morgan, R. A. Adenovirus-mediated expression of human coagulation factor IX in the rhesus macaque is associated with dose-limiting toxicity. Blood 94, 3968–3975 (1999).

[239]: Louis Jeune, V., Joergensen, J. A., Hajjar, R. J. & Weber, T. Pre-existing anti-adeno-associated virus antibodies as a challenge in AAV gene therapy. Hum. Gene Ther. Methods 24, 59–67 (2013).

[240]: Chandler, R. J., Sands, M. S. & Venditti, C. P. Recombinant adeno-associated viral integration and genotoxicity: insights from animal models. Hum. Gene Ther. 28, 314–322 (2017).

[241]: Li, C. & Samulski, R. J. Engineering adeno-associated virus vectors for gene therapy. Nat. Rev. Genet. 21, 255–272 (2020).

[242]: Greig, J. A. et al. Integrated vector genomes may contribute to long-term expression in primate liver after AAV administration. Nat. Biotechnol. 42, 1232–1242 (2024).

[243]: Lek, A. et al. Death after high-dose rAAV9 gene therapy in a patient with Duchenne’s muscular dystrophy. N. Engl. J. Med. 389, 1203–1210 (2023).

[244]: Karikó, K., Buckstein, M., Ni, H. & Weissman, D. Suppression of RNA recognition by Toll-like receptors: the impact of nucleoside modification and the evolutionary origin of RNA. Immunity 23, 165–175 (2005).

[245]: Polack, F. P. et al. Safety and efficacy of the BNT162b2 mRNA COVID-19 vaccine. N. Engl. J. Med. 383, 2603–2615 (2020).

[246]: Baden, L. R. et al. Efficacy and safety of the mRNA-1273 SARS-CoV-2 vaccine. N. Engl. J. Med. 384, 403–416 (2021).

[247]: Zhang, Y., Sun, C., Wang, C., Jankovic, K. E. & Dong, Y. Lipids and lipid derivatives for RNA delivery. Chem. Rev. 121, 12181–12277 (2021).

[248]: Cheng, Q. et al. Selective organ targeting (SORT) nanoparticles for tissue-specific mRNA delivery and CRISPR–Cas gene editing. Nat. Nanotechnol. 15, 313–320 (2020).

[249]: Dilliard, S. A., Cheng, Q. & Siegwart, D. J. On the mechanism of tissue-specific mRNA delivery by selective organ targeting nanoparticles. Proc. Natl Acad. Sci. USA 118, e2109256118 (2021).

[250]: Vavassori, V. et al. Lipid nanoparticles allow efficient and harmless ex vivo gene editing of human hematopoietic cells. Blood 142, 812–826 (2023).

[251]: Costa, C. et al. Mystery solved: VSV-G-LVs do not allow efficient gene transfer into unstimulated T cells, B cells, and HSCs because they lack the LDL receptor. Blood 123, 1422–1423 (2014).

[252]: Chen, R. et al. Engineering circular RNA for enhanced protein production. Nat. Biotechnol. 41, 262–272 (2023).

[253]: Chen, H. et al. Chemical and topological design of multicapped mRNA and capped circular RNA to augment translation. Nat. Biotechnol. https://doi.org/10.1038/s41587-024-02393-y (2024).

[254]: Chen, H. et al. Branched chemically modified poly(A) tails enhance the translation capacity of mRNA. Nat. Biotechnol. https://doi.org/10.1038/s41587-024-02174-7 (2024).

[255]: Gilleron, J. et al. Image-based analysis of lipid nanoparticle-mediated siRNA delivery, intracellular trafficking and endosomal escape. Nat. Biotechnol. 31, 638–646 (2013).

[256]: Androsavich, J. R. Frameworks for transformational breakthroughs in RNA-based medicines. Nat. Rev. Drug. Discov. 23, 421–444 (2024).

[257]: Dowdy, S. F. Endosomal escape of RNA therapeutics: how do we solve this rate-limiting problem? RNA 29, 396–401 (2023).

[258]: Sahay, G. et al. Efficiency of siRNA delivery by lipid nanoparticles is limited by endocytic recycling. Nat. Biotechnol. 31, 653–658 (2013).

[259]: Brown, D. W. et al. Safe and effective in vivo delivery of DNA and RNA using proteolipid vehicles. Cell 187, 1–19 (2024).

[260]: Zhang, Z. et al. Efficient engineering of human and mouse primary cells using peptide-assisted genome editing. Nat. Biotechnol. 42, 305–315 (2024).

[261]: Foss, D. V. et al. Peptide-mediated delivery of CRISPR enzymes for the efficient editing of primary human lymphocytes. Nat. Biomed. Eng. 7, 647–660 (2023).

[262]: Choi, J. G. et al. Lentivirus pre-packed with Cas9 protein for safer gene editing. Gene Ther. 23, 627–633 (2016).

[263]: Montagna, C. et al. VSV-G-enveloped vesicles for traceless delivery of CRISPR–Cas9. Mol. Ther. Nucleic Acids 12, 453–462 (2018).

[264]: Lyu, P., Javidi-Parsijani, P., Atala, A. & Lu, B. Delivering Cas9/sgRNA ribonucleoprotein (RNP) by lentiviral capsid-based bionanoparticles for efficient ‘hit-and-run’ genome editing. Nucleic Acids Res. 47, e99 (2019).

[265]: Mangeot, P. E. et al. Genome editing in primary cells and in vivo using viral-derived nanoblades loaded with Cas9–sgRNA ribonucleoproteins. Nat. Commun. 10, 45 (2019).

[266]: Hamilton, J. R. et al. Targeted delivery of CRISPR–Cas9 and transgenes enables complex immune cell engineering. Cell Rep. 35, 109207 (2021).

[267]: Banskota, S. et al. Engineered virus-like particles for efficient in vivo delivery of therapeutic proteins. Cell 185, 1–16 (2022).

[268]: An, M. et al. Engineered virus-like particles for transient delivery of prime editor ribonucleoprotein complexes in vivo. Nat. Biotechnol. 42, 1526–1537 (2024).

[269]: Finkelshtein, D., Werman, A., Novick, D., Barak, S. & Rubinstein, M. LDL receptor and its family members serve as the cellular receptors for vesicular stomatitis virus. Proc. Natl Acad. Sci. USA 110, 7306–7311 (2013).

[270]: Girard-Gagnepain, A. et al. Baboon envelope pseudotyped LVs outperform VSV-G-LVs for gene transfer into early-cytokine-stimulated and resting HSCs. Blood 124, 1221–1231 (2014).

[271]: Hamilton, J. R. et al. In vivo human T cell engineering with enveloped delivery vehicles. Nat. Biotechnol. 42, 1684–1692 (2024).

[272]: Car, T. et al. Rapid manufacturing of non-activated potent CAR T cells. Nat. Biomed. Eng. 6, 118–128 (2022).

[273]: Valeri, E. et al. Removal of innate immune barriers allows efficient transduction of quiescent human hematopoietic stem cells. Mol. Ther. 32, 124–139 (2024).

[274]: Zhang, P. et al. Schlafen 11 triggers innate immune responses through its ribonuclease activity upon detection of single-stranded DNA. Sci. Immunol. 9, eadj5465 (2024).

[275]: Liu, P. et al. Increasing intracellular dNTP levels improves prime editing efficiency. Nat. Biotechnol. https://doi.org/10.1038/s41587-024-02405-x (2024).

[276]: Liu, B. et al. Targeted genome editing with a DNA-dependent DNA polymerase and exogenous DNA-containing templates. Nat. Biotechnol. https://doi.org/10.1038/s41587-023-01947-w (2023).

[277]: da Silva, J. F. et al. Click editing enables programmable genome writing using DNA polymerases and HUH endonucleases. Nat. Biotechnol. https://doi.org/10.1038/s41587-024-02324-x (2024).

[278]: Nance, K. D. & Meier, J. L. Modifications in an emergency: the role of N1-methylpseudouridine in COVID-19 vaccines. ACS Cent. Sci. 7, 748–756 (2021).

[279]: McGee, J. E. et al. Complete substitution with modified nucleotides suppresses the early interferon response and increases the potency of self-amplifying RNA. Nat. Biotechnol. https://doi.org/10.1038/s41587-024-02306-z (2024).

[280]: Watson, J. The significance of the paucity of sickle cells in newborn Negro infants. Am. J. Med. Sci. 215, 419–423 (1948).

[281]: Lessard, S. et al. Zinc finger nuclease-mediated disruption of the BCL11A erythroid enhancer results in enriched biallelic editing, increased fetal hemoglobin, and reduced sickling in erythroid cells derived from sickle cell disease patients. Blood 134, 974–974 (2019).

[282]: Sharma, A. et al. CRISPR–Cas9 editing of the HBG1 and HBG2 promoters to treat sickle cell disease. N. Engl. J. Med. 389, 820–832 (2023).

[283]: De Dreuzy, E. et al. EDIT-301: an experimental autologous cell therapy comprising Cas12a-RNP modified mPB-CD34+ cells for the potential treatment of SCD. Blood 134, 4636–4636 (2019).
