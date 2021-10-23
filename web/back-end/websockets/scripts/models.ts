export type KeyValue = { key: string; value: string };

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

export function toIotDevices(devices: KeyValue[]): IotDevice[] {
    return devices.map((device) => {
        const id = device.key.replace('states/', '');
        const jsonValues = JSON.parse(device.value);
        const netId = id.split('/')[1];
        const urlId = id.replace('/', '-');
        const iotDevice = { id, urlId, netId, ...jsonValues };

        return iotDevice;
    });
}
