import { useEffect, useRef, useState } from "react";
import {
  UploadCloud,
  Info,
  Lightbulb,
  Play,
  Image,
  Settings,
  Search,
  List,
  Scan,
  BarChart3,
  FileCheck
} from "lucide-react";

import { getCategories, inspectImage } from "../services/api";

function NewInspection({
  token,
  onResult
}) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [categories, setCategories] =
    useState(["bottle"]);
  const [category, setCategory] =
    useState("bottle");
  const [loading, setLoading] =
    useState(false);
  const [error, setError] =
    useState("");

  const fileInput = useRef(null);

  useEffect(() => {
    getCategories()
      .then((data) => {
        if (data.categories?.length) {
          setCategories(data.categories);
          setCategory(data.categories[0]);
        }
      })
      .catch(() => {});
  }, []);

  const selectFile = (selected) => {
    if (!selected) return;

    setFile(selected);
    setPreview(
      URL.createObjectURL(selected)
    );
    setError("");
  };

  const handleDrop = (event) => {
    event.preventDefault();

    const dropped =
      event.dataTransfer.files?.[0];

    if (dropped) {
      selectFile(dropped);
    }
  };

  const runInspection = async () => {
    if (!file) {
      setError("Please upload a product image.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await inspectImage(
        file,
        category,
        token
      );

      onResult(data, preview);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    ["1", Image, "Upload Image"],
    ["2", Settings, "Image Preprocessing"],
    ["3", Search, "Anomaly Detection"],
    ["4", List, "Defect Classification"],
    ["5", Scan, "Defect Localization"],
    ["6", BarChart3, "Severity Analysis"],
    ["7", FileCheck, "Inspection Result"]
  ];

  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>New Inspection</h1>
          <p>
            Upload a product image to detect defects
            and analyze quality.
          </p>
        </div>
      </div>

      <div className="inspection-upload-grid">
        <section className="panel">
          <div
            className="drop-zone"
            onDragOver={(e) =>
              e.preventDefault()
            }
            onDrop={handleDrop}
            onClick={() =>
              fileInput.current?.click()
            }
          >
            <input
              ref={fileInput}
              type="file"
              accept=".jpg,.jpeg,.png,.bmp"
              hidden
              onChange={(e) =>
                selectFile(
                  e.target.files?.[0]
                )
              }
            />

            {preview ? (
              <img
                src={preview}
                alt="Selected product"
                className="upload-preview"
              />
            ) : (
              <>
                <UploadCloud size={55} />

                <strong>
                  Drag and drop an image here
                </strong>

                <span>or</span>

                <button
                  type="button"
                  className="choose-file-button"
                >
                  Choose File
                </button>

                <small>
                  Supported formats: JPG, PNG, BMP
                  | Max size: 10 MB
                </small>
              </>
            )}
          </div>
        </section>

        <aside className="guideline-card">
          <div className="guideline-title">
            <Info size={21} />
            <h3>Image Guidelines</h3>
          </div>

          <ul>
            <li>Use clear, well-lit images</li>
            <li>
              Ensure the product is fully visible
            </li>
            <li>
              Avoid blur or low-resolution images
            </li>
            <li>
              Supported formats: JPG, PNG, BMP
            </li>
            <li>Maximum file size: 10 MB</li>
          </ul>

          <div className="tip-box">
            <Lightbulb size={22} />

            <div>
              <strong>Tip</strong>
              <p>
                Good image quality leads to more
                accurate inspection results.
              </p>
            </div>
          </div>
        </aside>
      </div>

      <section className="panel inspection-settings">
        <h2>Inspection Settings</h2>

        <div className="settings-row">
          <div>
            <label>Product Category</label>

            <select
              value={category}
              onChange={(e) =>
                setCategory(e.target.value)
              }
            >
              {categories.map((item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item
                    .replaceAll("_", " ")
                    .replace(
                      /\b\w/g,
                      (char) =>
                        char.toUpperCase()
                    )}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label>Inspection Mode</label>

            <select defaultValue="standard">
              <option value="standard">
                Standard (Recommended)
              </option>
            </select>
          </div>

          <label className="quality-checkbox">
            <input
              type="checkbox"
              defaultChecked
            />
            Enable quality analysis
          </label>

          <button
            className="primary-button run-inspection"
            onClick={runInspection}
            disabled={loading}
          >
            <Play size={18} />

            {loading
              ? "Running..."
              : "Run Inspection"}
          </button>
        </div>

        {error && (
          <div className="form-error">
            {error}
          </div>
        )}
      </section>

      <section className="panel process-panel">
        <h2>Inspection Process</h2>

        <div className="process-flow">
          {steps.map(
            ([number, Icon, label], index) => (
              <div
                className="process-step"
                key={number}
              >
                <div className="step-number">
                  {number}
                </div>

                <Icon size={25} />

                <span>{label}</span>

                {index < steps.length - 1 && (
                  <div className="process-arrow">
                    →
                  </div>
                )}
              </div>
            )
          )}
        </div>
      </section>
    </div>
  );
}

export default NewInspection;