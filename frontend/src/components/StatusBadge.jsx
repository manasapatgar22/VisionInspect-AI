function StatusBadge({ status }) {
  const normalized = String(status || "")
    .toLowerCase();

  let className = "status-badge";

  if (normalized === "pass") {
    className += " pass";
  } else if (normalized === "fail") {
    className += " fail";
  } else {
    className += " review";
  }

  return (
    <span className={className}>
      {status || "UNKNOWN"}
    </span>
  );
}

export default StatusBadge;