export function apiErrorMessage(body, fallback) {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = body.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map(function (item) {
          return JSON.stringify(item);
        })
        .join("; ");
    }
  }
  return fallback;
}

export async function apiJson(url, options, fallback) {
  const res = await fetch(url, options);
  const body = await res.json().catch(function () {
    return {};
  });
  if (!res.ok) throw new Error(apiErrorMessage(body, fallback));
  return body;
}