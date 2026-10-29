type ComparisonIllustrationProps = {
  kind: "guidance" | "research";
  label: string;
};

export function ComparisonIllustration({ kind, label }: ComparisonIllustrationProps) {
  return (
    <div className={`comparisonIllustration comparisonIllustration--${kind}`} aria-hidden="true">
      {kind === "guidance" ? (
        <svg viewBox="0 0 64 64" fill="none" role="presentation">
          <path d="M12 17.5A7.5 7.5 0 0 1 19.5 10h25A7.5 7.5 0 0 1 52 17.5v18a7.5 7.5 0 0 1-7.5 7.5H31L20 52v-9h-.5a7.5 7.5 0 0 1-7.5-7.5v-18Z" />
          <path d="M23 24h18M23 31h12" />
          <circle cx="45" cy="47" r="8" />
          <path d="m42 47 2 2 4-5" />
        </svg>
      ) : (
        <svg viewBox="0 0 64 64" fill="none" role="presentation">
          <path d="M13 14h26a6 6 0 0 1 6 6v28H19a6 6 0 0 1-6-6V14Z" />
          <path d="M20 24h17M20 31h13M20 38h9" />
          <circle cx="45" cy="42" r="10" />
          <path d="m52.5 49.5 6 6" />
        </svg>
      )}
      <span>{label}</span>
    </div>
  );
}
