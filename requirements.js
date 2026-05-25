// ── Adam's graduation requirements ───────────────────────────────────────────
// Edit this file to update requirement buckets without touching the main app.

const FIXED_REQUIRED = new Set([
  'ARCH 2102','ARCH 2302','ARCH 2614','ARCH 2616',
  'ARCH 3101','ARCH 3102','ARCH 3302','ARCH 3615',
  'ARCH 4101','ARCH 4102','ARCH 5101','ARCH 5201',
  'ARCH 5902','ARCH 5911',
]);

const HUM_SS_CODES   = new Set(['ALC-AAP','SSC-AAP','CA-AG','HA-AG','KCM-AG','LA-AG','SBA-AG','ALC-AS','ETM-AS','GLC-AS','HST-AS','SCD-AS','SSC-AS','SSC-HA','CA-HE','HA-HE','KCM-HE','SBA-HE']);
const MATH_QR_CODES  = new Set(['MQR-AAP','MQL-AG','SDS-AS','SMR-AS','MQR-HE']);
const PHYS_BIO_CODES = new Set(['BIO-AG','OPHLS-AG','BIO-AS','PHS-AS','PBS-HE']);
const ART_STUDIO_IDS = new Set(['1201','1501','1504','1601','1602','1901','2201','2301','2401','2501','2601','2701','3011']);
const IN_COLLEGE_SUBJ = new Set(['ARCH','AAP','ART','CRP','DESIGN','REAL']);

const REQUIREMENTS = [
  // Type 1 — fixed required courses (exact match)
  { id: 'required',   label: 'Required',   badgeClass: 'badge-req1', type: 1,
    matches: r => FIXED_REQUIRED.has(r.courseId) },

  // Type 2 — elective pools (pattern match)
  { id: 'hist-arch',  label: 'Hist Arch',  badgeClass: 'badge-req',  type: 2,
    matches: r => r.subject === 'ARCH' && (
      r.catalogNbrNum === 5819 ||
      (r.catalogNbrNum >= 3800 && r.catalogNbrNum <= 3890) ||
      (r.catalogNbrNum >= 6800 && r.catalogNbrNum <= 6819)) },
  { id: 'theory',     label: 'Theory',     badgeClass: 'badge-req',  type: 2,
    matches: r => r.subject === 'ARCH' && ['3308','4300','6308','6319'].includes(r.catalogNbr) },
  { id: 'bldg-tech',  label: 'Bldg Tech',  badgeClass: 'badge-req',  type: 2,
    matches: r => r.subject === 'ARCH' && (
      ['3605','4601'].includes(r.catalogNbr) ||
      (r.catalogNbrNum >= 4600 && r.catalogNbrNum <= 4690)) },
  { id: 'arch-elec',  label: 'ARCH Elec',  badgeClass: 'badge-req',  type: 2,
    matches: r => r.subject === 'ARCH' },
  { id: 'art-studio', label: 'Art Studio', badgeClass: 'badge-req',  type: 2,
    matches: r => r.subject === 'ART' && ART_STUDIO_IDS.has(r.catalogNbr) },
  { id: 'in-college', label: 'In-College', badgeClass: 'badge-req',  type: 2,
    matches: r => IN_COLLEGE_SUBJ.has(r.subject) },

  // Type 3 — distribution attribute requirements
  { id: 'hum-ss',     label: 'Hum/SS',     badgeClass: 'badge-req',  type: 3,
    matches: r => r.distrReqs.some(c => HUM_SS_CODES.has(c)) },
  { id: 'math-qr',    label: 'Math/QR',    badgeClass: 'badge-req',  type: 3,
    matches: r => r.distrReqs.some(c => MATH_QR_CODES.has(c)) },
  { id: 'phys-bio',   label: 'Phys/Bio',   badgeClass: 'badge-req',  type: 3,
    matches: r => r.distrReqs.some(c => PHYS_BIO_CODES.has(c)) },
];

const REQ_BY_ID = Object.fromEntries(REQUIREMENTS.map(r => [r.id, r]));
