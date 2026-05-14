const CONTENT_TYPE_ALIASES: Record<string, string> = {
  "image/jpg": "image/jpeg",
  "video/m4v": "video/x-m4v",
};

const FALLBACK_CONTENT_TYPES = {
  photo: {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
  },
  video: {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".m4v": "video/x-m4v",
  },
} as const;

type MediaUploadKind = keyof typeof FALLBACK_CONTENT_TYPES;

function getExtension(filename: string) {
  const dotIndex = filename.lastIndexOf(".");
  return dotIndex >= 0 ? filename.slice(dotIndex).toLowerCase() : "";
}

export function normalizeMediaContentType(file: File, kind: MediaUploadKind) {
  const rawContentType = file.type.split(";", 1)[0]?.trim().toLowerCase();
  if (rawContentType) {
    return CONTENT_TYPE_ALIASES[rawContentType] ?? rawContentType;
  }

  const fallbackContentTypes = FALLBACK_CONTENT_TYPES[kind] as Record<string, string>;
  const fallbackContentType = fallbackContentTypes[getExtension(file.name)];
  if (fallbackContentType) {
    return fallbackContentType;
  }

  throw new Error(`Unable to determine the ${kind} file content type`);
}

export async function uploadFileToPresignedUrl(uploadUrl: string, file: File, contentType: string) {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    headers: {
      "Content-Type": contentType,
    },
    body: file,
  });

  if (response.ok) {
    return;
  }

  const responseText = (await response.text()).trim();
  throw new Error(responseText || `Upload failed with status ${response.status}`);
}
