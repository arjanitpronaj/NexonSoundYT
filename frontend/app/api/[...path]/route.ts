import { NextRequest, NextResponse } from "next/server";

import { getBackendUrl } from "@/utils/backend";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const targetUrl = `${getBackendUrl()}/${path.join("/")}${request.nextUrl.search}`;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("content-type", contentType);
  }
  const accept = request.headers.get("accept");
  if (accept) {
    headers.set("accept", accept);
  }

  const init: RequestInit = {
    method: request.method,
    headers,
    cache: "no-store",
  };

  if (!["GET", "HEAD"].includes(request.method)) {
    init.body = await request.arrayBuffer();
  }

  try {
    const response = await fetch(targetUrl, init);
    const responseHeaders = new Headers();
    const passthrough = ["content-type", "content-disposition", "content-length"];
    passthrough.forEach((name) => {
      const value = response.headers.get(name);
      if (value) {
        responseHeaders.set(name, value);
      }
    });

    return new NextResponse(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch {
    return NextResponse.json(
      { detail: "Backend is unreachable. Wait for Render to wake up, then try again." },
      { status: 502 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
