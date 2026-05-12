const YOUTUBE_REGEX =
  /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|shorts\/|embed\/|live\/)|youtu\.be\/|music\.youtube\.com\/watch\?v=)[\w-]+/i;

export function isValidYouTubeUrl(url: string): boolean {
  return YOUTUBE_REGEX.test(url.trim());
}

export function normalizeInputUrl(url: string): string {
  return url.trim();
}
