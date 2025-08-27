// front11/src/types.ts

export type VehicleResponse = {
  vin: string;
  make: string;
  model: string;
  year: number | null;
  bodyType: string;
  fuelType: string;
  manufacturer: string;
  plantCountry: string;
  lastSix?: string;
};