"""
This script (created by Copilot) generates a synthetic dataset of 2000 lung cancer
patients with realistic distributions of demographics, tumor characteristics,
treatments, and outcomes. The data is designed to reflect known epidemiological
patterns and clinical relationships in lung cancer, while also incorporating
random variation and noise. The resulting dataset is saved as 'synthetic_lung_cancer.csv'
and can be used for testing predictive models, simulating clinical scenarios, or educational purposes.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(42)
N = 2000

def choice(pairs, size):
    vals, probs = zip(*pairs)
    probs = np.array(probs, dtype=float)
    probs = probs / probs.sum()
    idx = rng.choice(len(vals), size=size, p=probs)
    return np.array(vals, dtype=object)[idx]

# --- Demographics ---
sex = choice([('F', 0.46), ('M', 0.54)], N)
age = np.clip(rng.normal(67, 9.5, N).round().astype(int), 35, 90)
race = choice([('White', 0.68), ('Black', 0.13), ('Asian', 0.06), ('Hispanic', 0.09), ('Other', 0.04)], N)

smoking_status = choice([('Never', 0.18), ('Former', 0.57), ('Current', 0.25)], N)
pack_years = np.zeros(N)
pack_years[smoking_status == 'Never'] = rng.gamma(1.0, 1.0, (smoking_status == 'Never').sum())
pack_years[smoking_status != 'Never'] = rng.gamma(6.0, 6.0, (smoking_status != 'Never').sum())
pack_years = np.clip(pack_years, 0, 120)

bmi = np.clip(rng.normal(27.2, 5.2, N), 16, 45)
comorbidity_index = np.clip(rng.poisson(2.0, N) + (age > 75).astype(int), 0, 12)
ecog = np.clip(rng.choice([0,1,2,3,4], size=N, p=[0.20,0.36,0.26,0.14,0.04]) + (age>78).astype(int), 0, 4)

# Diagnosis date between 2015 and 2025 inclusive
years = rng.integers(2015, 2026, size=N)
base_dates = [datetime(int(y), 1, 1) for y in years]
days_into_year = rng.integers(0, 365, size=N)
diagnosis_date = np.array([bd + timedelta(days=int(d)) for bd, d in zip(base_dates, days_into_year)], dtype='datetime64[ns]')

dx_series = pd.Series(pd.to_datetime(diagnosis_date))

# --- Tumor characteristics ---
stage = choice([('I', 0.18), ('II', 0.16), ('III', 0.30), ('IV', 0.36)], N)
stage_num = pd.Series(stage).map({'I':1,'II':2,'III':3,'IV':4}).to_numpy()

histology = choice([('Adenocarcinoma', 0.55), ('Squamous', 0.25), ('SmallCell', 0.12), ('OtherNSCLC', 0.08)], N)
is_small_cell = (histology == 'SmallCell').astype(int)

never = (smoking_status == 'Never')
aden = (histology == 'Adenocarcinoma')

p_egfr = np.clip(0.16 + 0.12*never + 0.06*aden - 0.05*(sex=='M'), 0.02, 0.45)
p_alk  = np.clip(0.05 + 0.05*never + 0.03*aden, 0.01, 0.20)
p_kras = np.clip(0.22 + 0.08*aden + 0.05*(smoking_status!='Never'), 0.05, 0.55)

egfr_mut = (rng.random(N) < p_egfr)
alk_fusion = (rng.random(N) < p_alk)
kras_mut = (rng.random(N) < p_kras)

pdl1_percent = np.clip(rng.beta(1.6, 3.2, N)*100 + 6*(stage_num-2) + 4*(smoking_status=='Current'), 0, 100)

true_tumor_size = rng.normal(2.0 + 1.2*(stage_num-1), 0.9, N)
tumor_size_cm = np.clip(true_tumor_size + rng.normal(0, 0.4, N), 0.3, 12.0)

# --- Labs near diagnosis ---
lab_offset_days = rng.integers(-14, 15, size=N)
lab_dt = dx_series + pd.to_timedelta(lab_offset_days, unit='D')
lab_date_near_dx = lab_dt.dt.date.astype(str)

inflammation = 0.55*(stage_num-1) + 0.35*ecog + 0.15*comorbidity_index + 0.10*(pack_years/20.0) + rng.normal(0, 0.9, N)

# Lung-related marker: CEA (ng/mL)
cea_ng_ml = np.exp(1.0 + 0.35*(stage_num-1) + 0.25*(histology=='Adenocarcinoma') + 0.10*(smoking_status!='Never') + rng.normal(0, 0.55, N))
cea_ng_ml = np.clip(cea_ng_ml, 0.2, 200)

ldh_u_l = np.clip(200 + 35*inflammation + 18*(stage_num-1) + rng.normal(0, 25, N), 90, 900)
albumin_g_dl = np.clip(4.1 - 0.18*inflammation + rng.normal(0, 0.22, N), 2.0, 5.5)
wbc_10e9_l = np.clip(6.5 + 0.55*inflammation + 0.25*(smoking_status=='Current') + rng.normal(0, 1.3, N), 1.5, 30)
hgb_g_dl = np.clip(13.4 - 0.35*inflammation - 0.15*is_small_cell + rng.normal(0, 1.1, N), 7.5, 18.0)
crp_mg_l = np.clip(np.exp(1.7 + 0.32*inflammation + rng.normal(0, 0.6, N)), 0.2, 250)
creatinine_mg_dl = np.clip(0.85 + 0.012*(age-60) + 0.04*comorbidity_index + rng.normal(0, 0.15, N), 0.4, 3.5)

# --- Treatments ---
p_surgery = np.clip(0.62 - 0.18*(stage_num-1) - 0.20*is_small_cell - 0.05*(ecog>=3), 0.02, 0.75)
had_surgery = (rng.random(N) < p_surgery).astype(int)

surgery_type = np.array(['None']*N, dtype=object)
mask_surg = had_surgery == 1
surgery_type[mask_surg] = choice([('Wedge', 0.18), ('Segmentectomy', 0.14), ('Lobectomy', 0.54), ('Pneumonectomy', 0.10), ('SleeveResection', 0.04)], mask_surg.sum())

p_radiation = np.clip(0.20 + 0.12*(stage_num-1) + 0.08*(had_surgery==0) + 0.06*(histology=='SmallCell'), 0.05, 0.90)
had_radiation = (rng.random(N) < p_radiation).astype(int)

p_chemo = np.clip(0.30 + 0.16*(stage_num-1) + 0.22*(histology=='SmallCell') + 0.05*(ecog<=2), 0.05, 0.95)
had_chemo = (rng.random(N) < p_chemo).astype(int)

chemo_type = np.array(['None']*N, dtype=object)
mask_chemo = had_chemo == 1
p_targeted = (egfr_mut | alk_fusion) & (histology != 'SmallCell')
p_immuno = (pdl1_percent >= 50) & (histology != 'SmallCell')

for i in np.where(mask_chemo)[0]:
    if p_targeted[i] and rng.random() < 0.70:
        chemo_type[i] = 'Targeted_EGFR' if egfr_mut[i] else 'Targeted_ALK'
    elif p_immuno[i] and rng.random() < 0.55:
        chemo_type[i] = 'Immunotherapy_PD1'
    else:
        if histology[i] == 'SmallCell':
            chemo_type[i] = rng.choice(['Platinum_Etoposide', 'Carboplatin_Etoposide'], p=[0.55,0.45])
        else:
            chemo_type[i] = rng.choice(['Platinum_Pemetrexed', 'Platinum_Paclitaxel', 'Platinum_Gemcitabine'], p=[0.42,0.35,0.23])

radiation_dose_gy = np.where(had_radiation==1, np.clip(rng.normal(55 + 6*(stage_num-2), 8, N), 20, 74), 0.0)
chemo_cycles = np.where(had_chemo==1, np.clip(rng.normal(4.5 + 0.6*(stage_num-2) - 0.5*(ecog>=3), 1.2, N), 1, 8).round(), 0)

# --- Outcomes (survival + censoring) ---
ldh_z = (ldh_u_l - ldh_u_l.mean())/ldh_u_l.std()
alb_z = (albumin_g_dl - albumin_g_dl.mean())/albumin_g_dl.std()
crp_z = (np.log1p(crp_mg_l) - np.log1p(crp_mg_l).mean())/np.log1p(crp_mg_l).std()

risk = (
    0.03*(age-65) + 0.85*(stage_num-2.2) + 0.55*(ecog-1.2) + 0.22*(comorbidity_index-2) +
    0.25*(pack_years/30.0) + 0.55*ldh_z - 0.45*alb_z + 0.25*crp_z -
    0.35*had_surgery - 0.22*had_chemo - 0.15*had_radiation + 0.25*(histology=='SmallCell') +
    rng.normal(0, 0.85, N)
)

# Weibull survival; higher risk -> shorter survival
k_shape = 1.35
base_scale = 1200
scale = np.clip(base_scale * np.exp(-0.55*risk), 60, 4000)

u = rng.random(N)
survival_days_true = (scale * (-np.log(u))**(1.0/k_shape))

# Administrative censoring
admin_end = np.datetime64('2026-03-01')
max_followup_days = (admin_end - diagnosis_date).astype('timedelta64[D]').astype(int)
max_followup_days = np.clip(max_followup_days, 30, 4500)

# Random loss to follow-up
ltfu_propensity = 0.10 + 0.06*(age>78) + 0.05*(stage_num==4) + 0.04*(ecog>=3)
ltfu = rng.random(N) < np.clip(ltfu_propensity, 0.05, 0.30)
ltfu_time = rng.uniform(30, 0.95*max_followup_days, N)

obs_time = np.minimum(survival_days_true, max_followup_days.astype(float))
obs_time = np.where(ltfu, np.minimum(obs_time, ltfu_time), obs_time)

vital_status = np.where(survival_days_true <= obs_time + 1e-9, 'Deceased', 'Alive')
days_to_death_or_ltfu = obs_time.round().astype(int)
one_year_mortality = (survival_days_true <= 365).astype(int)

# --- Build dataset ---
df = pd.DataFrame({
    'patient_id': [f'LC{str(i).zfill(6)}' for i in range(1, N+1)],
    'diagnosis_date': dx_series.dt.date.astype(str),
    'age_at_diagnosis': age,
    'sex': sex,
    'race_ethnicity': race,
    'smoking_status': smoking_status,
    'pack_years': np.round(pack_years, 1),
    'bmi': np.round(bmi, 1),
    'comorbidity_index': comorbidity_index,
    'ecog': ecog,
    'stage': stage,
    'stage_num': stage_num,
    'histology': histology,
    'egfr_mut': egfr_mut.astype(int),
    'alk_fusion': alk_fusion.astype(int),
    'kras_mut': kras_mut.astype(int),
    'pdl1_percent': np.round(pdl1_percent, 1),
    'tumor_size_cm': np.round(tumor_size_cm, 2),

    'lab_date_near_dx': lab_date_near_dx,
    'cea_ng_ml': np.round(cea_ng_ml, 2),
    'ldh_u_l': np.round(ldh_u_l, 0).astype(int),
    'albumin_g_dl': np.round(albumin_g_dl, 2),
    'wbc_10e9_l': np.round(wbc_10e9_l, 2),
    'hemoglobin_g_dl': np.round(hgb_g_dl, 2),
    'crp_mg_l': np.round(crp_mg_l, 2),
    'creatinine_mg_dl': np.round(creatinine_mg_dl, 2),

    'had_surgery': had_surgery,
    'surgery_type': surgery_type,
    'had_radiation': had_radiation,
    'radiation_dose_gy': np.round(radiation_dose_gy, 1),
    'had_chemo': had_chemo,
    'chemo_type': chemo_type,
    'chemo_cycles': chemo_cycles.astype(int),

    'days_to_death_or_ltfu': days_to_death_or_ltfu,
    'vital_status': vital_status,
    'one_year_mortality': one_year_mortality,

    'inflammation_index': np.round(inflammation, 2),
    'risk_score_latent': np.round(risk, 3)
})

# Add realistic missingness (slightly more missing in stage IV)
for col, miss_base in [('cea_ng_ml', 0.08), ('crp_mg_l', 0.12), ('pdl1_percent', 0.10)]:
    miss = rng.random(N) < np.clip(miss_base + 0.04*(stage_num==4), 0.02, 0.25)
    df.loc[miss, col] = np.nan

df.to_csv('synthetic_lung_cancer.csv', index=False)
print("Wrote synthetic_lung_cancer.csv", df.shape)
