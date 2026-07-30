// OctoAvatar project interaction logic
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const elements = {
  dropzone: $("#dropzone"),
  fileInput: $("#fileInput"),
  pickButton: $("#pickButton"),
  editor: $("#editor"),
  replaceButton: $("#replaceButton"),
  canvas: $("#previewCanvas"),
  canvasWrap: $("#canvasWrap"),
  zoom: $("#zoomRange"),
  zoomValue: $("#zoomValue"),
  rotateLeft: $("#rotateLeft"),
  rotateRight: $("#rotateRight"),
  reset: $("#resetButton"),
  size: $("#sizeSelect"),
  download: $("#downloadButton"),
  status: $("#status"),
  sizeStatus: $("#sizeStatus")
};

const state = {
  image: null,
  fileName: "github-avatar",
  scale: 1,
  offsetX: 0,
  offsetY: 0,
  rotation: 0,
  dragging: false,
  pointerX: 0,
  pointerY: 0,
  shape: "square"
};

const MAX_BYTES = 1024 * 1024;

["dragenter", "dragover"].forEach((eventName) => {
  elements.dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropzone.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  elements.dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropzone.classList.remove("dragging");
  });
});

elements.dropzone.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  if (file) loadFile(file);
});

elements.pickButton.addEventListener("click", () => elements.fileInput.click());
elements.replaceButton.addEventListener("click", () => elements.fileInput.click());
elements.fileInput.addEventListener("change", () => {
  const file = elements.fileInput.files[0];
  if (file) loadFile(file);
  elements.fileInput.value = "";
});

async function loadFile(file) {
  setStatus("正在识别并读取图片…");
  try {
    let source = file;
    const extension = file.name.split(".").pop().toLowerCase();
    if (["heic", "heif"].includes(extension) || /hei[cf]/i.test(file.type)) {
      if (typeof heic2any !== "function") {
        throw new Error("HEIC 转换组件加载失败，请联网后重试");
      }
      source = await heic2any({ blob: file, toType: "image/png", quality: 0.92 });
      if (Array.isArray(source)) source = source[0];
    }

    const bitmap = await decodeImage(source);
    if (!bitmap.width || !bitmap.height) throw new Error("图片内容无法识别");
    state.image?.close?.();
    state.image = bitmap;
    state.fileName = file.name.replace(/\.[^.]+$/, "") || "github-avatar";
    resetTransform();
    elements.dropzone.hidden = true;
    elements.editor.hidden = false;
    setStatus(`已读取 ${bitmap.width} × ${bitmap.height}，可以调整并导出`);
    elements.editor.scrollIntoView({ behavior: "smooth", block: "center" });
  } catch (error) {
    setStatus(`无法读取：${error.message}`, true);
  }
}

async function decodeImage(blob) {
  if ("createImageBitmap" in window) {
    try {
      return await createImageBitmap(blob, { imageOrientation: "from-image" });
    } catch (_) {
      // Safari and some image formats use the fallback below.
    }
  }
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(blob);
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("当前浏览器不支持此格式，请先转换为 PNG、JPG 或 WebP"));
    };
    img.src = url;
  });
}

function resetTransform() {
  state.rotation = 0;
  state.offsetX = 0;
  state.offsetY = 0;
  state.scale = 1;
  elements.zoom.value = 100;
  elements.zoomValue.value = "100%";
  draw();
}

function rotatedDimensions() {
  const quarterTurn = Math.abs(state.rotation / 90) % 2 === 1;
  return {
    width: quarterTurn ? state.image.height : state.image.width,
    height: quarterTurn ? state.image.width : state.image.height
  };
}

function draw(target = elements.canvas, targetSize = target.width) {
  if (!state.image) return;
  const targetCtx = target.getContext("2d", { alpha: false });
  const { width, height } = rotatedDimensions();
  const baseScale = Math.max(targetSize / width, targetSize / height);
  const actualScale = baseScale * state.scale;
  const ratio = targetSize / elements.canvas.width;

  targetCtx.save();
  targetCtx.fillStyle = "#ffffff";
  targetCtx.fillRect(0, 0, targetSize, targetSize);
  targetCtx.translate(targetSize / 2 + state.offsetX * ratio, targetSize / 2 + state.offsetY * ratio);
  targetCtx.rotate(state.rotation * Math.PI / 180);
  targetCtx.scale(actualScale, actualScale);
  targetCtx.imageSmoothingEnabled = true;
  targetCtx.imageSmoothingQuality = "high";
  targetCtx.drawImage(state.image, -state.image.width / 2, -state.image.height / 2);
  targetCtx.restore();
}

elements.zoom.addEventListener("input", () => {
  state.scale = Number(elements.zoom.value) / 100;
  elements.zoomValue.value = `${elements.zoom.value}%`;
  draw();
});

elements.canvasWrap.addEventListener("wheel", (event) => {
  event.preventDefault();
  const next = Math.min(400, Math.max(100, Number(elements.zoom.value) - Math.sign(event.deltaY) * 10));
  elements.zoom.value = next;
  elements.zoom.dispatchEvent(new Event("input"));
}, { passive: false });

elements.canvasWrap.addEventListener("pointerdown", (event) => {
  state.dragging = true;
  state.pointerX = event.clientX;
  state.pointerY = event.clientY;
  elements.canvasWrap.setPointerCapture(event.pointerId);
});

elements.canvasWrap.addEventListener("pointermove", (event) => {
  if (!state.dragging) return;
  const scale = elements.canvas.width / elements.canvasWrap.clientWidth;
  state.offsetX += (event.clientX - state.pointerX) * scale;
  state.offsetY += (event.clientY - state.pointerY) * scale;
  state.pointerX = event.clientX;
  state.pointerY = event.clientY;
  draw();
});

const stopDragging = () => { state.dragging = false; };
elements.canvasWrap.addEventListener("pointerup", stopDragging);
elements.canvasWrap.addEventListener("pointercancel", stopDragging);

elements.rotateLeft.addEventListener("click", () => {
  state.rotation = (state.rotation - 90) % 360;
  state.offsetX = state.offsetY = 0;
  draw();
});

elements.rotateRight.addEventListener("click", () => {
  state.rotation = (state.rotation + 90) % 360;
  state.offsetX = state.offsetY = 0;
  draw();
});

elements.reset.addEventListener("click", resetTransform);

$$(".shape-button").forEach((button) => {
  button.addEventListener("click", () => {
    $$(".shape-button").forEach((item) => {
      item.classList.remove("active");
      item.setAttribute("aria-pressed", "false");
    });
    button.classList.add("active");
    button.setAttribute("aria-pressed", "true");
    state.shape = button.dataset.shape;
    elements.canvasWrap.classList.toggle("circle", state.shape === "circle");
  });
});

function canvasToBlob(canvas) {
  return new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
}

async function createCompliantPng() {
  let dimension = Math.min(Number(elements.size.value), 2999);
  let output = document.createElement("canvas");
  output.width = output.height = dimension;
  draw(output, dimension);
  let blob = await canvasToBlob(output);

  while (blob && blob.size >= MAX_BYTES && dimension > 128) {
    dimension = Math.max(128, Math.floor(dimension * 0.88));
    const smaller = document.createElement("canvas");
    smaller.width = smaller.height = dimension;
    smaller.getContext("2d").drawImage(output, 0, 0, dimension, dimension);
    output = smaller;
    blob = await canvasToBlob(output);
  }

  if (!blob || blob.size >= MAX_BYTES) {
    throw new Error("无法保持 PNG 格式并压缩到 1 MB 以下，请换一张图片");
  }
  return { blob, dimension };
}

elements.download.addEventListener("click", async () => {
  if (!state.image) return;
  elements.download.disabled = true;
  setStatus("正在生成并校验 PNG…");
  try {
    const { blob, dimension } = await createCompliantPng();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${state.fileName}-github-avatar.png`;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    const kb = Math.ceil(blob.size / 1024);
    elements.sizeStatus.textContent = `${kb} KB`;
    setStatus(`导出成功：PNG · ${dimension} × ${dimension} · ${kb} KB`);
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    elements.download.disabled = false;
  }
});

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.style.color = isError ? "#b42318" : "";
}
