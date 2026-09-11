import { Search } from "lucide-react";
import { useMemo, useState } from "react";

import InspectionTable from "../components/InspectionTable";

function InspectionHistory({
  inspections,
  onView
}) {
  const [search, setSearch] =
    useState("");

  const filtered = useMemo(() => {
    const value =
      search.toLowerCase().trim();

    if (!value) return inspections;

    return inspections.filter((item) =>
      [
        item.filename,
        item.category,
        item.defect_type,
        item.decision,
        item.severity_level
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(value)
    );
  }, [inspections, search]);

  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>Inspection History</h1>
          <p>
            View and review previous inspection
            records.
          </p>
        </div>
      </div>

      <section className="panel">
        <div className="history-toolbar">
          <div className="search-box">
            <Search size={18} />

            <input
              placeholder="Search inspections..."
              value={search}
              onChange={(e) =>
                setSearch(e.target.value)
              }
            />
          </div>

          <span className="record-count">
            {filtered.length} records
          </span>
        </div>

        <InspectionTable
          inspections={filtered}
          onView={onView}
        />
      </section>
    </div>
  );
}

export default InspectionHistory;