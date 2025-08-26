// front11/src/types.ts

export type VehicleResponse = {
  VIN: string;
  Make: string;
  Model: string;
  ModelYear: string;
  BodyClass: string;
  VehicleType: string;
  EngineCylinders: string;
  FuelTypePrimary: string;
  PlantCountry: string;
  lastSix?: string; // Optional in case it’s injected manually
  [key: string]: string | undefined;
};