import styles from './device.module.css';
import { useHistory } from 'react-router-dom';
import { Card } from '../card';
import { Tag } from '../tag';
import { DeviceType } from '@declarations';

type Props = { device: DeviceType };

export function Device(props: Props) {
    const { device } = props;
    const history = useHistory();

    return (
        <div
            className={`${styles.component} m-5`}
            onClick={() => history.push(`/devices/${device.id}`)}
        >
            <Card>
                <>
                    <div>Name: {device.name}</div>
                    <div>IP: {device.ip}</div>
                    <div>Type: {device.type}</div>
                    <div>State: {device.state}</div>
                    <div className="flex">
                        {device.tags.map((tag) => (
                            <Tag key={tag} label={tag} />
                        ))}
                    </div>
                </>
            </Card>
        </div>
    );
}
