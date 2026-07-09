from CRABClient.UserUtilities import config
config = config()
config.General.requestName = 'EWKZ2Jets_ZToQQ_DIGI_test_FNAL_'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'EWKZ2Jets_ZToQQ_DIGI_cfg_.py'
config.JobType.numCores = 2
config.JobType.maxMemoryMB = 5000
config.Data.inputDBS = 'phys03'
config.Data.inputDataset = '/EWKZ2Jets_ZToQQ_FNAL/sapradha-GENSIM_test_v2-804c2017e1ed687af3d8f15b1df490f9/USER'   # <-- fill in real hash, see below
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
config.Data.publication = True
config.Data.outputDatasetTag = 'DIGI_test_v2'
config.Data.outLFNDirBase = '/store/user/sapradha/VBFHBB/EWK_Z2Q/'

config.Site.storageSite = 'T3_US_FNALLPC'
