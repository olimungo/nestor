export enum DeviceTypes {
    SHADE,
    SIGN,
    SWITCH,
    CLOCK,
}

export type DeviceType = {
    id: string;
    name: string;
    ip: string;
    type: string;
    state: string;
    tags: string[];
};

export type DevicesByTagsType = {
    id: number;
    code: string;
    label: string;
    devices: DeviceType[];
};

export function getDeviceTypeLabel(type: number) {
    switch (type) {
        case DeviceTypes.SHADE:
            return 'SHADE';
        case DeviceTypes.SIGN:
            return 'SIGN';
        case DeviceTypes.SWITCH:
            return 'SWITCH';
        case DeviceTypes.CLOCK:
            return 'CLOCK';
        default:
            return '';
    }
}

export function getDeviceTypeCode(type: number) {
    switch (type) {
        case DeviceTypes.SHADE:
            return 'SHADE';
        case DeviceTypes.SIGN:
            return 'SIGN';
        case DeviceTypes.SWITCH:
            return 'SWITCH';
        case DeviceTypes.CLOCK:
            return 'CLOCK';
        default:
            return '';
    }
}
