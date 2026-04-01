import { describe, it, expect } from "vitest";
import { formatApiError } from "./apiErrors";

function axiosLike(status, detail) {
  return {
    response: { status, data: { detail } },
  };
}

describe("formatApiError", () => {
  it("joins validation error array detail", () => {
    const err = axiosLike(422, [{ msg: "campo requerido" }, { foo: "bar" }]);
    expect(formatApiError(err)).toBe('campo requerido; {"foo":"bar"}');
  });

  it("returns plain string detail when present", () => {
    expect(formatApiError(axiosLike(400, "Solicitud inválida."))).toBe("Solicitud inválida.");
  });

  it("prefixes string detail for 403, 404, 502, 503", () => {
    expect(formatApiError(axiosLike(403, "No admin"))).toBe("Acceso denegado (403): No admin");
    expect(formatApiError(axiosLike(404, "Missing"))).toBe("No encontrado (404): Missing");
    expect(formatApiError(axiosLike(502, "Bad gateway"))).toBe(
      "Respuesta inválida del servidor (502): Bad gateway",
    );
    expect(formatApiError(axiosLike(503, "Cuota"))).toBe(
      "Servicio externo no disponible temporalmente (503): Cuota",
    );
  });

  it("uses status defaults when detail is missing", () => {
    expect(formatApiError(axiosLike(401, undefined))).toBe("No autenticado (401). Inicie sesión de nuevo.");
    expect(formatApiError(axiosLike(403, undefined))).toBe("Acceso denegado (403).");
    expect(formatApiError(axiosLike(404, undefined))).toBe("Recurso no encontrado (404).");
    expect(formatApiError(axiosLike(503, undefined))).toBe(
      "Servicio de IA temporalmente no disponible (503). Reintente en 1-2 minutos.",
    );
    expect(formatApiError(axiosLike(502, undefined))).toBe(
      "El servidor devolvió una respuesta no válida (502). Reintente.",
    );
  });

  it("appends fallback for other 5xx without string detail", () => {
    const fb = "Intente más tarde.";
    expect(formatApiError(axiosLike(500, null), { fallback: fb })).toBe(
      "Error interno del servidor (500). Intente más tarde.",
    );
    expect(formatApiError(axiosLike(529, undefined), { fallback: fb })).toBe(
      "Error interno del servidor (529). Intente más tarde.",
    );
  });

  it("uses err.message or fallback when no response", () => {
    expect(formatApiError(new Error("Network down"), { fallback: "fb" })).toBe("Network down");
    expect(formatApiError({}, { fallback: "solo fb" })).toBe("solo fb");
  });

  it("uses default Spanish fallback", () => {
    expect(formatApiError({})).toBe("Ha ocurrido un error. Intente de nuevo.");
  });

  it("ignores whitespace-only string detail", () => {
    expect(formatApiError(axiosLike(500, "   "), { fallback: "fb" })).toContain("Error interno");
  });
});
