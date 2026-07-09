from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'EWKZ2Jets_ZToQQ_RECO_test'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'EWKZ2Jets_ZToQQ_RECO_cfg.py'
config.JobType.numCores = 2
config.JobType.maxMemoryMB = 5000
config.Data.inputDBS = 'phys03'
config.Data.inputDataset = '/EWKZ2Jets_ZToQQ_FNAL/sapradha-DIGI_test_v2-245bc4b12a0ac5d7498981ce54a22f17/USER'   # <-- fill in after step2 finishes

config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
config.Data.publication = True
config.Data.outputDatasetTag = 'RECO_test_v1'
config.Data.outLFNDirBase = '/store/user/sapradha/VBFHBB/EWK_Z2Q/'

config.Site.storageSite = 'T3_US_FNALLPC'
