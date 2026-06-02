const form = document.querySelector("#stats-form");
const dataInput = document.querySelector("#data-input");
const techniqueSelect = document.querySelector("#technique");
const kField = document.querySelector("#k-field");
const kInput = document.querySelector("#k-input");
const resetButton = document.querySelector("#reset-button");
const results = document.querySelector("#results");
const emptyState = document.querySelector("#empty-state");
const resultTitle = document.querySelector("#result-title");
const metadata = document.querySelector("#metadata");
const formulas = document.querySelector("#formulas");
const steps = document.querySelector("#steps");
const frequencyBody = document.querySelector("#frequency-body");
const validations = document.querySelector("#validations");
const themeToggle = document.querySelector("#theme-toggle");
const themeIcon = document.querySelector(".theme-icon");
const fileInput = document.querySelector("#file-input");
const fileDropZone = document.querySelector("#file-drop-zone");

// File Import Handlers
function extractNumbersFromSheet(sheet) {
  const numbers = [];
  if (!sheet) return numbers;

  for (const key in sheet) {
    if (key === "!ref" || key === "!margins") continue;
    const cell = sheet[key];
    if (cell && cell.v !== undefined) {
      const value = parseFloat(cell.v);
      if (!isNaN(value)) {
        numbers.push(value);
      }
    }
  }
  return numbers;
}

function handleCSV(text) {
  const lines = text.split(/[\n\r]+/);
  const numbers = [];

  for (const line of lines) {
    const values = line.split(/[,;\t]/);
    for (const val of values) {
      const num = parseFloat(val.trim());
      if (!isNaN(num)) {
        numbers.push(num);
      }
    }
  }

  return numbers;
}

function handleFileUpload(file) {
  if (!file) return;

  const fileName = file.name.toLowerCase();
  if (!fileName.match(/\.(xlsx|xls|csv)$/)) {
    alert("Por favor sube un archivo Excel o CSV (.xlsx, .xls, .csv)");
    return;
  }

  fileDropZone.classList.add("loading");

  const reader = new FileReader();
  reader.onload = function (e) {
    try {
      // Si es CSV, procesa directamente como texto
      if (fileName.endsWith(".csv")) {
        const text = e.target.result;
        const allNumbers = handleCSV(text);

        if (allNumbers.length === 0) {
          alert("No se encontraron números en el archivo.");
          fileDropZone.classList.remove("loading");
          return;
        }

        dataInput.value = allNumbers.join(", ");
        dataInput.focus();
        fileDropZone.title = `✓ Cargados ${allNumbers.length} números`;

        setTimeout(() => {
          fileDropZone.title = "";
          fileDropZone.classList.remove("loading");
        }, 2000);
        return;
      }

      // Para Excel, usa XLSX si está disponible
      if (typeof XLSX === "undefined") {
        alert(
          "La librería de Excel no se cargó. Por favor intenta:\n1. Recargar la página\n2. Usar un archivo CSV en lugar de Excel"
        );
        fileDropZone.classList.remove("loading");
        return;
      }

      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: "array" });

      let allNumbers = [];

      // Procesar todas las hojas
      for (const sheetName of workbook.SheetNames) {
        const worksheet = workbook.Sheets[sheetName];
        const numbers = extractNumbersFromSheet(worksheet);
        allNumbers = allNumbers.concat(numbers);
      }

      if (allNumbers.length === 0) {
        alert("No se encontraron números en el archivo. Por favor verifica que contenga datos numéricos.");
        fileDropZone.classList.remove("loading");
        return;
      }

      // Llenar el textarea con los números encontrados
      dataInput.value = allNumbers.join(", ");
      dataInput.focus();

      fileDropZone.title = `✓ Cargados ${allNumbers.length} números`;

      setTimeout(() => {
        fileDropZone.title = "";
        fileDropZone.classList.remove("loading");
      }, 2000);
    } catch (error) {
      console.error("Error:", error);
      alert("Error al procesar el archivo: " + error.message);
      fileDropZone.classList.remove("loading");
    }
  };

  if (fileName.endsWith(".csv")) {
    reader.readAsText(file);
  } else {
    reader.readAsArrayBuffer(file);
  }
}

// File drop zone events
fileDropZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    handleFileUpload(e.target.files[0]);
  }
});

// Drag and drop
fileDropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  fileDropZone.classList.add("drag-over");
});

fileDropZone.addEventListener("dragleave", () => {
  fileDropZone.classList.remove("drag-over");
});

fileDropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  fileDropZone.classList.remove("drag-over");
  
  if (e.dataTransfer.files.length > 0) {
    handleFileUpload(e.dataTransfer.files[0]);
  }
});

// Theme Management
function initializeTheme() {
  const savedTheme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIconDisplay(savedTheme);
}

function updateThemeIcon(theme) {
  themeToggle.textContent = theme === "dark" ? "☀️" : "🌙";
}

function updateThemeIconDisplay(theme) {
  const icon = theme === "dark" ? "☀" : "☾";
  if (themeIcon) {
    themeIcon.textContent = icon;
    return;
  }
  themeToggle.textContent = icon;
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  updateThemeIconDisplay(newTheme);
}

themeToggle.addEventListener("click", toggleTheme);

function updateKVisibility() {
  kField.hidden = techniqueSelect.value !== "arbitrary";
}

function clearResults() {
  results.hidden = true;
  emptyState.hidden = false;
  resultTitle.textContent = "";
  metadata.innerHTML = "";
  formulas.innerHTML = "";
  steps.innerHTML = "";
  frequencyBody.innerHTML = "";
  validations.innerHTML = "";
}

function showError(message) {
  results.hidden = false;
  emptyState.hidden = true;
  resultTitle.textContent = "No se pudo generar la tabla";
  metadata.innerHTML = "";
  formulas.innerHTML = "";
  steps.innerHTML = "";
  frequencyBody.innerHTML = "";
  validations.innerHTML = `<div class="error-banner">${escapeHtml(message)}</div>`;
}

function renderResult(result) {
  results.hidden = false;
  emptyState.hidden = true;
  resultTitle.textContent = result.technique;

  metadata.innerHTML = Object.entries(result.metadata)
    .filter(([key]) => shouldShowMetadata(key, result.metadata))
    .map(([key, value]) => `<span class="chip">${escapeHtml(formatMetadataKey(key))}: ${escapeHtml(formatMetadataValue(value))}</span>`)
    .join("");

  formulas.innerHTML = result.formulas.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  steps.innerHTML = result.steps.map((item) => `<li>${escapeHtml(item)}</li>`).join("");

  frequencyBody.innerHTML = result.rows
    .map(
      (row) => `
        <tr>
          <td>${escapeHtml(row.intervalo)}</td>
          <td>${row.fi}</td>
          <td>${row.hi.toFixed(3)}</td>
          <td>${row.pi.toFixed(2)}</td>
          <td>${row.Fi}</td>
          <td>${row.Hi.toFixed(3)}</td>
          <td>${row.Pi.toFixed(2)}</td>
        </tr>
      `,
    )
    .join("");

  validations.innerHTML = result.validations
    .filter((validation) => shouldShowValidation(validation.name))
    .map(
      (validation) => `
        <div class="validation ${validation.ok ? "" : "error"}">
          <strong>${escapeHtml(validation.name)}</strong>
          <span>${escapeHtml(validation.message)}</span>
        </div>
      `,
    )
    .join("");
}

function shouldShowValidation(name) {
  const hiddenValidations = new Set([
    "Primer intervalo incluye dato mínimo",
    "Último intervalo incluye dato máximo",
    "Sin intervalos vacíos en extremos",
    "Todos los datos están clasificados",
  ]);
  return !hiddenValidations.has(name);
}

function shouldShowMetadata(key, currentMetadata) {
  const hiddenKeys = new Set(["correction_applied", "cobertura"]);
  const groupedAliasKeys = new Set(["d", "D", "la"]);
  if (currentMetadata.d_original !== undefined && groupedAliasKeys.has(key)) {
    return false;
  }
  return !hiddenKeys.has(key);
}

function formatMetadataKey(key) {
  const labels = {
    n: "n",
    d: "d",
    D: "D",
    c: "c",
    K: "K",
    t: "t",
    d_original: "d original",
    D_original: "D original",
    d_corrected: "d corregido",
    D_corrected: "D corregido",
    la: "Longitud del alcance",
    la_original: "Longitud original",
    la_corrected: "Longitud corregida",
    leftover: "Sobrante",
    valores_distintos: "Valores distintos",
  };
  return labels[key] || key.replaceAll("_", " ");
}

function formatMetadataValue(value) {
  if (typeof value === "boolean") {
    return value ? "Sí" : "No";
  }
  return value;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

techniqueSelect.addEventListener("change", updateKVisibility);

resetButton.addEventListener("click", () => {
  form.reset();
  updateKVisibility();
  clearResults();
  dataInput.focus();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    data: dataInput.value,
    technique: techniqueSelect.value,
    k: kInput.value,
  };

  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();

    if (!body.ok) {
      showError(body.error || "Error desconocido.");
      return;
    }
    renderResult(body.result);
  } catch (error) {
    showError("No fue posible comunicarse con el servidor.");
  }
});

updateKVisibility();
initializeTheme();
