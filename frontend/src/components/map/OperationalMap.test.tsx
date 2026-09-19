import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { OperationalMap } from "./OperationalMap";

const { mapConstructor, mapInstance } = vi.hoisted(() => {
  const instance = {
    jumpTo: vi.fn(),
    on: vi.fn(),
    remove: vi.fn(),
    resize: vi.fn(),
    zoomIn: vi.fn(),
    zoomOut: vi.fn(),
  };
  return { mapConstructor: vi.fn(() => instance), mapInstance: instance };
});

vi.mock("maplibre-gl", () => ({ Map: mapConstructor }));

class TestResizeObserver {
  disconnect = vi.fn();
  observe = vi.fn();
}

beforeEach(() => {
  Object.values(mapInstance).forEach((value) => {
    if (typeof value === "function" && "mockClear" in value) value.mockClear();
  });
  vi.stubGlobal("ResizeObserver", TestResizeObserver);
});

afterEach(() => {
  cleanup();
  mapConstructor.mockClear();
  vi.unstubAllGlobals();
});

describe("OperationalMap", () => {
  it("initializes a neutral map without operational layers and exposes map controls", () => {
    render(<OperationalMap />);

    expect(mapConstructor).toHaveBeenCalledWith(expect.objectContaining({
      attributionControl: false,
      center: [0, -82],
      maxBounds: [[-180, -90], [180, -45]],
      zoom: 1.65,
    }));
    expect(screen.getByText("Operational layers are unavailable until validated geospatial services are connected.")).toBeInTheDocument();
    expect(screen.getByText("Operational layers unavailable")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Zoom in" }));
    fireEvent.click(screen.getByRole("button", { name: "Zoom out" }));
    fireEvent.click(screen.getByRole("button", { name: "Focus Antarctica" }));

    expect(mapInstance.zoomIn).toHaveBeenCalledOnce();
    expect(mapInstance.zoomOut).toHaveBeenCalledOnce();
    expect(mapInstance.jumpTo).toHaveBeenCalledWith({ center: [0, -82], zoom: 1.65 });
  });

  it("reports initialization failure without rendering operational data", () => {
    mapConstructor.mockImplementationOnce(() => { throw new Error("WebGL unavailable"); });
    render(<OperationalMap />);

    expect(screen.getByText("Operational map unavailable")).toBeInTheDocument();
    expect(screen.getByText("The map foundation could not be initialized. No operational layers are displayed.")).toBeInTheDocument();
  });
});
