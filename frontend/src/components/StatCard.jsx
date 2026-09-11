function StatCard({
  icon,
  value,
  label,
  percentage,
  type = "blue"
}) {
  return (
    <div className="stat-card-new">
      <div className={`stat-icon ${type}`}>
        {icon}
      </div>

      <div className="stat-content">
        <strong>{value}</strong>

        <span>{label}</span>

        {percentage !== undefined && (
          <small>{percentage}</small>
        )}
      </div>
    </div>
  );
}

export default StatCard;