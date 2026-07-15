# Private MC Production: EWKZ2Jets_ZToQQ (Run3 2022 postEE)

---

## 1. Login and CMSSW setup

```bash
ssh -X <your_username>@lxplus8.cern.ch
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_12_4_11_patch3
cd CMSSW_12_4_11_patch3/src
cmsenv
voms-proxy-init --voms cms --valid 192:00
```

Place the GEN fragment under `Configuration/GenProduction/python/` and
`scram b -j 4` before running any local `cmsDriver.py` step.

---

## 2. Gridpack tarball in CRAB

The gridpack tarball must be shipped explicitly via `inputFiles`, and
referenced with a `../` prefix inside the fragment/cfg — the gridpack-unpack
script (`run_generic_tarball_cvmfs.sh`) creates and `cd`s into a `lheevent/`
subdirectory before untarring, so the path must be given relative to that.

```python
config.JobType.inputFiles = ['EWKZ2Jets_ZToQQ_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz']
```
```python
args = cms.vstring('../EWKZ2Jets_ZToQQ_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz'),
```

Keep the tarball in the same directory you run `crab submit` from.

---

## 3. Avoid duplicate events

**Do not hardcode the LHE seed.** Leave out (or comment out) any
`initialSeed` override for `externalLHEProducer`:

```python
# do NOT set this for production:
# process.RandomNumberGeneratorService.externalLHEProducer.initialSeed = 1
```

CRAB's `PrivateMC` job type automatically assigns each job its own
randomized seed so that parallel jobs generate distinct, non-overlapping
events. A hardcoded seed defeats that — at best it's redundant, at worst
every job generates the *same* events, silently wasting the entire
production. There's no legitimate reason to fix this seed for a real
production campaign, so just don't set it.

---

## 4. Local testing tips

- **GEN-SIM step** (generates new events from the gridpack): `-n` controls
  how many events to *generate* for the test — a small number (e.g. `100`)
  is fine and fast.
- **Any step reading a fixed input file** (DIGI, RECO, MiniAOD, ...): use
  `-n -1` instead of a fixed number, so `cmsRun` processes every event in
  your local test file rather than an arbitrary subset. This also matches
  what actually happens once submitted to CRAB — `FileBased` splitting
  processes each job's assigned input file(s) in full regardless of what
  `-n` was baked into the cfg.

---

## 5. Scaling to large (e.g. 1M event) production

- Confirm the seed override is commented out (Section 3) — critical at scale.
- In step 1's config: raise `unitsPerJob`/`totalUnits` to reach the target
  event count; size `unitsPerJob` against your local run's wall-clock time
  per event (aim for each job to run a few hours, well under the 24h grid
  limit).
- Give every step a fresh `outputDatasetTag` for the full run (distinct from
  any test tag), to avoid overwriting/colliding with test datasets in DBS.
- Steps 2–4 scale automatically via `FileBased` splitting on the prior
  step's output — only their `inputDataset` needs updating each time.
  **This requires write access to a real CMS storage element** (see below);
  it will not work while output is staged only on CERNBox.

---

## 6. Storage note: `T3_CH_CERNBOX` limitation

`T3_CH_CERNBOX` can only be used as a final **output** destination.
CERNBox is not a real CMS storage element, so files written there cannot be
listed in DBS, moved by Rucio, or read back as a later CRAB task's
`inputDataset` — CRAB will refuse such a submission (`SUBMITREFUSED`).

For a small number of files, this can be worked around with
`config.Data.userInputFiles` (explicit list of `root://eosuser.cern.ch/...`
paths, bypassing DBS/site-locality matching). This does **not** scale to a
1M-event, multi-hundred-file production. For the full run, get write access
to a proper Tier-2/3 storage element with Rucio registration so `inputDataset`
chaining works normally at every step.


# Anatomy of a CMS Dataset Name

A quick reference for decoding CMS Monte Carlo dataset names, using a real
example from DBS (Dataset Bookkeeping Service).

## Example Dataset

```
/VBFZto2Q_TuneCP5_13p6TeV_madgraph-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2/MINIAODSIM
```

Every CMS dataset name follows the fixed structure:

```
/PrimaryDataset/ProcessedDataset/DataTier
```

---

## 1. Primary Dataset — `VBFZto2Q_TuneCP5_13p6TeV_madgraph-pythia8`

Describes the physics process and generator configuration.

| Component | Meaning |
|---|---|
| `VBFZto2Q` | Physics process: VBF-produced Z boson decaying to two quarks (Z→qq̄) |
| `TuneCP5` | Pythia8 tune — see below |
| `13p6TeV` | Center-of-mass collision energy (Run 3 LHC) |
| `madgraph-pythia8` | Generator chain: MadGraph (hard matrix element) + Pythia8 (shower/hadronization) |

### TuneCP5 — what a "tune" is

Parton-shower/hadronization generators like Pythia8 have many free parameters
that aren't calculable from first-principles QCD: color reconnection, the
multiple-parton-interaction rate, initial/final-state radiation amount, and
hadronization details. These are fit ("tuned") to real collider data.

**CP5** specifics:
- Fitted using LHC underlying-event and minimum-bias measurements, combined
  with the **NNPDF3.1 NLO** PDF set.
- Supersedes earlier tunes such as **CUETP8M1** used in early Run 2.
- "CP" denotes tunes developed with CMS/Pythia collaboration input, as
  opposed to generic Monash-style tunes.
- Two samples sharing the same tune are guaranteed identical
  shower/hadronization/underlying-event modeling — important when combining
  signal and background MC in an analysis, since tune mismatches are a
  known source of subtle systematic mismodeling.

---

## 2. Processed Dataset — `Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6_ext1-v2`

Describes the production campaign, software, and conditions. All of this is
packed into one field (DBS only allows 3 slash-separated fields), separated
by hyphens.

| Sub-component | Value | Meaning |
|---|---|---|
| Campaign name | `Run3Summer22EE` | Run 3, "Summer22" campaign; "EE" = post-ECAL-Endcap-change period of 2022 |
| Output tier stage | `MiniAODv4` | 4th reprocessing version of MiniAOD for this campaign |
| CMSSW release | `130X` | Software release series: `CMSSW_13_0_X` |
| Global Tag | `mcRun3_2022_realistic_postEE_v6` | Detector alignment/calibration conditions snapshot, version 6 — equivalent to the `--conditions` flag in `cmsDriver.py` |
| Extension | `ext1` | Additional events added later to boost statistics |
| Version | `v2` | 2nd processing/submission of this dataset (v1 was superseded) |

---

## 3. Data Tier — `MINIAODSIM`

Confirms this is simulated (`SIM`) data at the MiniAOD tier — the compact,
analysis-ready format produced by the PAT step.

---

## Relating this to detector conditions and pileup

- **Detector conditions** for the signal sample are captured entirely in the
  Global Tag field (`mcRun3_2022_realistic_postEE_v6`).
- **Pileup is not part of this dataset's name at all.** It comes from a
  separate premix dataset referenced via `--pileup_input`, e.g.:

  ```
  /Neutrino_E-10_gun/Run3Summer21PrePremix-Summer22_124X_mcRun3_2022_realistic_v11-v2/PREMIX
  ```

  - `Neutrino_E-10_gun` — a neutrino-gun sample used purely as a carrier for
    pre-mixed pileup hits (neutrinos don't interact with the detector, so
    this wastes no meaningful physics content).
  - The processed-dataset field here has its **own, independently versioned**
    conditions tag (`124X_..._v11`), which can differ from the signal
    sample's tag — pileup libraries are generated once and reused across
    many different signal productions.
  - Data tier `PREMIX` — pre-combined pileup hits/digis ready to be mixed
    into any signal sample's DIGI/DATAMIX step.

So a full MC sample's provenance is really governed by **two independently
tracked conditions**: the signal sample's Global Tag, and the pileup
library's Global Tag — both feeding into the final MINIAODSIM.

---

## Mapping to a `cmsDriver.py` command

| Dataset component | `cmsDriver.py` equivalent |
|---|---|
| `VBFZto2Q_..._madgraph-pythia8` | GEN fragment (gridpack + Pythia8 tune settings) |
| `13p6TeV` | Implicit in `--era Run3` |
| `Run3Summer22EE` | `--era Run3`, postEE conditions |
| `130X_mcRun3_2022_realistic_postEE_v6` | `--conditions <global tag>` |
| `MINIAODSIM` | `--datatier MINIAODSIM`, `--step ...,PAT` |
| Pileup premix dataset | `--pileup_input dbs:/.../PREMIX` |
