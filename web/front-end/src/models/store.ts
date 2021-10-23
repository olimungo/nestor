import { IotDevice, IotDeviceGroup } from '@models';

export type Store = {
    devices: IotDevice[];
    selectedGroup: IotDeviceGroup | undefined;
};

export const StoreInit: Store = {
    devices: [],
    selectedGroup: undefined,
};
