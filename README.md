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
