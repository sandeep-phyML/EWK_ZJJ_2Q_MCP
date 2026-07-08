cmsDriver.py step2 \
--python_filename EWKZ2Jets_ZToQQ_DIGI_cfg.py \
--eventcontent PREMIXRAW \
--datatier GEN-SIM-RAW \
--fileout file:EWKZ2Jets_ZToQQ_DIGI.root \
--pileup_input "dbs:/Neutrino_E-10_gun/Run3Summer21PrePremix-Summer22_124X_mcRun3_2022_realistic_v11-v2/PREMIX" \
--conditions 124X_mcRun3_2022_realistic_postEE_v1 \
--step DIGI,DATAMIX,L1,DIGI2RAW,HLT:2022v14 \
--procModifiers premix_stage2 \
--geometry DB:Extended \
--filein file:EWKZ2Jets_ZToQQ_GENSIM.root \
--datamix PreMix \
--era Run3 \
--no_exec \
--mc \
-n 100


