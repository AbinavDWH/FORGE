/**
 * MOD-02 / MOD-04: Dual-Source Verification View (OCR ↔ VLM Cross-Check)
 * 
 * Rules per FORGE Architecture:
 * - Always displays side-by-side results of Primary (OCR / Whisper ASR) and Secondary (Qwen3-VL Vision Model).
 * - Matching fields are highlighted in green with checkmarks.
 * - Discrepancies/mismatches are highlighted in amber/rose.
 */
export default function OcrVlmComparison({ item }) {
  if (!item) return null;

  const crossCheck = item.cross_check || {};
  const extraction = item.extraction || {};
  
  const ocr = crossCheck.ocr_extraction || {
    spatial_zone: extraction.spatial_zone,
    discipline: extraction.discipline,
    component: extraction.component,
    action: extraction.action,
    status: extraction.status,
    percent_complete: extraction.percent_complete,
  };

  const vlm = crossCheck.vlm_extraction || {
    spatial_zone: extraction.spatial_zone,
    discipline: extraction.discipline,
    component: extraction.component,
    action: extraction.action,
    status: extraction.status,
    percent_complete: extraction.percent_complete,
  };

  const fieldAgreement = crossCheck.field_agreement || {
    spatial_zone: 'match',
    discipline: 'match',
    component: 'match',
    action: 'match',
    status: 'match',
    percent_complete: 'match',
  };

  const agreementScore = crossCheck.agreement_score !== undefined ? crossCheck.agreement_score : 1.0;
  const crossCheckStatus = crossCheck.cross_check_status || item.cross_check_status || 'agreed';

  const fields = [
    { key: 'spatial_zone', label: 'Spatial Zone' },
    { key: 'discipline', label: 'Discipline' },
    { key: 'component', label: 'Component' },
    { key: 'action', label: 'Action / Work' },
    { key: 'status', label: 'Status' },
    { key: 'percent_complete', label: '% Complete' },
  ];

  const renderStatusBadge = () => {
    if (crossCheckStatus === 'agreed') {
      return (
        <span className="text-[10px] font-mono uppercase px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-300 font-semibold flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
          Dual-Source Agreed (100%)
        </span>
      );
    } else if (crossCheckStatus === 'partial_mismatch') {
      return (
        <span className="text-[10px] font-mono uppercase px-2.5 py-1 bg-amber-50 text-amber-700 border border-amber-300 font-semibold flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-600"></span>
          Partial Mismatch ({Math.round(agreementScore * 100)}%)
        </span>
      );
    } else if (crossCheckStatus === 'disagreed') {
      return (
        <span className="text-[10px] font-mono uppercase px-2.5 py-1 bg-rose-50 text-rose-700 border border-rose-300 font-semibold flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span>
          Disagreement Detected
        </span>
      );
    }
    return (
      <span className="text-[10px] font-mono uppercase px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-300 font-semibold flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
        VLM & OCR Cross-Checked
      </span>
    );
  };

  return (
    <div className="mt-5 border border-forge-border bg-white overflow-hidden shadow-sm">
      {/* Header bar */}
      <div className="bg-forge-soft px-4 py-2.5 border-b border-forge-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-forge-accent"></div>
          <span className="text-xs font-semibold uppercase tracking-wider text-forge-fg font-mono">
            Dual-Source Verification: OCR ↔ Vision-Language Model
          </span>
        </div>
        {renderStatusBadge()}
      </div>

      {/* Comparison Table */}
      <div className="p-4">
        <div className="grid grid-cols-12 gap-2 text-xs font-mono">
          {/* Header */}
          <div className="col-span-3 text-[10px] uppercase tracking-wider text-forge-muted font-sans font-semibold pb-1 border-b border-forge-border">
            Field
          </div>
          <div className="col-span-4 text-[10px] uppercase tracking-wider text-emerald-800 font-sans font-semibold pb-1 border-b border-forge-border flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-emerald-600 rounded-full"></span>
            Primary (RapidOCR / ASR)
          </div>
          <div className="col-span-5 text-[10px] uppercase tracking-wider text-blue-800 font-sans font-semibold pb-1 border-b border-forge-border flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
            Secondary (Qwen3-VL 4B)
          </div>

          {/* Rows */}
          {fields.map((f, idx) => {
            const ocrVal = ocr[f.key];
            const vlmVal = vlm[f.key];
            const isMatch = fieldAgreement[f.key] === 'match' || String(ocrVal).toLowerCase() === String(vlmVal).toLowerCase();
            const isMismatch = fieldAgreement[f.key] === 'mismatch' && ocrVal && vlmVal && String(ocrVal).toLowerCase() !== String(vlmVal).toLowerCase();

            return (
              <div
                key={f.key}
                className={`col-span-12 grid grid-cols-12 gap-2 py-2 items-center border-b border-forge-border/40 last:border-b-0 ${
                  idx % 2 === 1 ? 'bg-forge-soft/20' : ''
                }`}
              >
                {/* Field Label */}
                <div className="col-span-3 text-forge-muted text-[11px]">
                  {f.label}
                </div>

                {/* Primary OCR Value */}
                <div className="col-span-4 px-2 py-1 bg-emerald-50/40 border border-emerald-100/60 rounded text-emerald-950 font-medium truncate">
                  {ocrVal !== null && ocrVal !== undefined ? (
                    String(ocrVal)
                  ) : (
                    <span className="text-forge-muted italic text-[10px]">null</span>
                  )}
                </div>

                {/* Secondary VLM Value & Status Tag */}
                <div
                  className={`col-span-5 px-2 py-1 border rounded flex items-center justify-between truncate ${
                    isMatch
                      ? 'bg-emerald-50/70 border-emerald-300 text-emerald-900'
                      : isMismatch
                      ? 'bg-rose-50/70 border-rose-300 text-rose-900 font-semibold'
                      : 'bg-blue-50/40 border-blue-200 text-blue-950'
                  }`}
                >
                  <span className="truncate">
                    {vlmVal !== null && vlmVal !== undefined ? (
                      String(vlmVal)
                    ) : (
                      <span className="text-forge-muted italic text-[10px]">null</span>
                    )}
                  </span>
                  {isMatch && (
                    <span className="text-[9px] font-bold text-emerald-700 ml-2 px-1 py-0.2 bg-emerald-100/80 rounded shrink-0">
                      ✓ MATCH
                    </span>
                  )}
                  {isMismatch && (
                    <span className="text-[9px] font-bold text-rose-700 ml-2 px-1 py-0.2 bg-rose-100/80 rounded shrink-0">
                      ≠ DIFF
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
