export default function MatchExplanationPanel({ matchResult }) {
  if (!matchResult) {
    return null;
  }

  const pct = (value) => `${Math.round((value || 0) * 100)}%`;

  return (
    <section className="border border-gray-200 bg-white p-4">
      <h3 className="font-mono text-[11px] uppercase tracking-widest text-gray-500">
        Match Explanation
      </h3>

      <p className="mt-2 font-mono text-sm text-gray-900">
        {matchResult.match_reason}
      </p>

      <div className="mt-3 grid grid-cols-2 gap-2 md:grid-cols-4">
        <div className="border border-gray-200 p-2 font-mono text-xs">
          <div className="text-gray-500">MATCH</div>
          <div className="mt-1 text-gray-900">
            {pct(matchResult.match_score)}
          </div>
        </div>

        <div className="border border-gray-200 p-2 font-mono text-xs">
          <div className="text-gray-500">SEMANTIC</div>
          <div className="mt-1 text-gray-900">
            {pct(matchResult.semantic_score)}
          </div>
        </div>

        <div className="border border-gray-200 p-2 font-mono text-xs">
          <div className="text-gray-500">FUZZY</div>
          <div className="mt-1 text-gray-900">
            {pct(matchResult.fuzzy_score)}
          </div>
        </div>

        <div className="border border-gray-200 p-2 font-mono text-xs">
          <div className="text-gray-500">CONTEXT</div>
          <div className="mt-1 text-gray-900">
            {pct(matchResult.context_score)}
          </div>
        </div>
      </div>

      {matchResult.match_score < 0.5 && (
        <div className="mt-3 border border-rose-600 px-2 py-1 font-mono text-xs text-rose-600">
          LOW CONFIDENCE — HUMAN REVIEW REQUIRED
        </div>
      )}
    </section>
  );
}