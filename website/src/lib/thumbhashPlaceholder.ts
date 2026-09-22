import { thumbHashToDataURL } from "thumbhash";

const HEX_PATTERN = /^[\da-f]+$/i;

function parseHexToBytes(hex: string): Uint8Array | undefined {
  const normalizedHex = hex.trim();

  if (normalizedHex.length === 0 || normalizedHex.length % 2 !== 0) {
    return undefined;
  }

  if (!HEX_PATTERN.test(normalizedHex)) {
    return undefined;
  }

  const bytes = new Uint8Array(normalizedHex.length / 2);

  for (let index = 0; index < bytes.length; index += 1) {
    const byte = Number.parseInt(normalizedHex.slice(index * 2, index * 2 + 2), 16);

    if (Number.isNaN(byte)) {
      return undefined;
    }

    bytes[index] = byte;
  }

  return bytes;
}

export function thumbhashHexToDataUrl(hex: string): string | undefined {
  const bytes = parseHexToBytes(hex);

  if (!bytes) {
    return undefined;
  }

  try {
    return thumbHashToDataURL(bytes);
  } catch {
    return undefined;
  }
}
