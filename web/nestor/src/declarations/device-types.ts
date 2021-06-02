export enum DeviceTypes {
    STEPPER_H,
    STEPPER_V,
    MOTOR_H,
    MOTOR_V,
    SWITCH,
    DOUBLE_SWITCH,
    SLIDER,
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
        case DeviceTypes.STEPPER_H:
            return 'STEPPER HORIZONTAL';
        case DeviceTypes.STEPPER_V:
            return 'STEPPER VERTICAL';
        case DeviceTypes.MOTOR_H:
            return 'MOTOR HORIZONTAL';
        case DeviceTypes.MOTOR_V:
            return 'MOTOR VERTICAL';
        case DeviceTypes.SWITCH:
            return 'SWITCH';
        case DeviceTypes.DOUBLE_SWITCH:
            return 'SWITCH (DOUBLE)';
        case DeviceTypes.SLIDER:
            return 'SLIDER';
        default:
            return '';
    }
}

export function getDeviceTypeCode(type: number) {
    switch (type) {
        case DeviceTypes.STEPPER_H:
            return 'STEPPER-H';
        case DeviceTypes.STEPPER_V:
            return 'STEPPER-V';
        case DeviceTypes.MOTOR_H:
            return 'MOTOR-H';
        case DeviceTypes.MOTOR_V:
            return 'MOTOR-V';
        case DeviceTypes.SWITCH:
            return 'SWITCH';
        case DeviceTypes.DOUBLE_SWITCH:
            return 'DOUBLE-SWITCH';
        case DeviceTypes.SLIDER:
            return 'SLIDER';
        default:
            return '';
    }
}
