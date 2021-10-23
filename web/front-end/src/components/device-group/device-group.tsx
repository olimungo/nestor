import styles from './device-group.module.css';
import { IotDeviceGroup } from '@models';
import { Card, Button } from '@components';

type Props = {
    iotDeviceGroup: IotDeviceGroup;
    onSelected?: (iotDeviceGroup: IotDeviceGroup) => void;
};

export function DeviceGroup(props: Props) {
    const dummyCallback = () => true;
    const { iotDeviceGroup, onSelected = dummyCallback } = props;

    return (
        <div className={`${styles.component} text-white m-5`}>
            <Card>
                <div className="flex justify-between" onClick={() => onSelected(iotDeviceGroup)}>
                    <div>
                        <div>{iotDeviceGroup.type}</div>

                        <div className="flex flex-wrap">
                            {iotDeviceGroup.devices.map((device) => (
                                <div
                                    className="m-2 bg-blue-500 rounded-lg p-2 w-12 text-center"
                                    key={device.id}
                                >
                                    {device.netId}
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="self-center">
                        <Button icon="chevron-right" iconSize="2x" />
                    </div>
                </div>
            </Card>
        </div>
    );
}
