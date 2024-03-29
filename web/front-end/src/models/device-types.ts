export const IotDeviceTypes = ['SHADE', 'SIGN', 'SWITCH', 'CLOCK'] as const;
export type IotDeviceType = typeof IotDeviceTypes[number];

export type IotDevice = {
    id: string;
    urlId: string;
    netId: string;
    type: IotDeviceType;
    ip: string;
    state: string;
    tags: string[];
};

export type IotDeviceGroup = {
    type: IotDeviceType;
    devices: IotDevice[];
};

export type IotDevicesByTags = {
    id: number;
    code: string;
    label: string;
    devices: IotDevice[];
};

export type IotDeviceById = { id: string; netId: string; selected: boolean };
