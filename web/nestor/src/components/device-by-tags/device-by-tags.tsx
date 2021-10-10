import styles from './device-by-tags.module.css';
import { DevicesByTagsType } from '@models';
import { Card, Button } from '@components';

type Props = {
    devicesByTags: DevicesByTagsType;
    onControl?: (selectedDevices: DevicesByTagsType) => void;
};

export function DeviceByTags(props: Props) {
    const dummyCallback = () => true;
    const { devicesByTags, onControl: onDetail = dummyCallback } = props;

    return (
        <div className={`${styles.component} text-white m-5`}>
            <Card>
                <div className="flex justify-between" onClick={() => onDetail(devicesByTags)}>
                    <div>
                        <div>{devicesByTags.code}</div>

                        <div className="flex flex-wrap">
                            {devicesByTags.devices.map((device) => (
                                <div className="m-2 bg-blue-500 rounded-lg p-2" key={device.id}>
                                    {device.id}
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="self-center">
                        <Button
                            icon="chevron-right"
                            iconSize="2x"
                            onClick={() => onDetail(devicesByTags)}
                        />
                    </div>
                </div>
            </Card>
        </div>
    );
}
