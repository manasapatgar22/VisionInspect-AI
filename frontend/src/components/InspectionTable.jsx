import { Eye } from "lucide-react";
import StatusBadge from "./StatusBadge";

function InspectionTable({
  inspections = [],
  onView
}) {
  return (
    <div className="table-wrapper">
      <table className="inspection-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Filename</th>
            <th>Category</th>
            <th>Defect Type</th>
            <th>Result</th>
            <th>Severity</th>
            <th>Date & Time</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {inspections.length === 0 ? (
            <tr>
              <td
                colSpan="8"
                className="table-empty"
              >
                No inspections found.
              </td>
            </tr>
          ) : (
            inspections.map((inspection) => (
              <tr key={inspection.id}>
                <td>#{String(inspection.id).padStart(3, "0")}</td>

                <td className="filename-cell">
                  {inspection.filename}
                </td>

                <td>
                  {inspection.category || "-"}
                </td>

                <td>
                  {inspection.defect_type || "-"}
                </td>

                <td>
                  <StatusBadge
                    status={inspection.decision}
                  />
                </td>

                <td>
                  {inspection.severity_level || "-"}
                </td>

                <td>
                  {inspection.created_at
                    ? new Date(
                        inspection.created_at
                      ).toLocaleString()
                    : "-"}
                </td>

                <td>
                  <button
                    className="table-action"
                    onClick={() =>
                      onView?.(inspection)
                    }
                    title="View inspection"
                  >
                    <Eye size={18} />
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default InspectionTable;