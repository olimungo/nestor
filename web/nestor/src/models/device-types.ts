// export type IotDeviceTypes = 'SHADE' | 'SIGN' | 'SWITCH' | 'CLOCK';

export const IotDeviceTypes = ['SHADE', 'SIGN', 'SWITCH', 'CLOCK'] as const;
export type IotDeviceType = typeof IotDeviceTypes[number];

export type IotDevice = {
    id: string;
    netId: string;
    type: IotDeviceType;
    ip: string;
    state: string;
    tags: string[];
};

export type DevicesByTagsType = {
    id: string;
    code: string;
    label: string;
    devices: IotDevice[];
};