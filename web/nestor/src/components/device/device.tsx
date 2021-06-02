import styles from './device.module.css';
import { useHistory } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExternalLinkAlt } from '@fortawesome/free-solid-svg-icons';
import { DeviceType } from '@declarations';
import { Card, Tag, ButtonEdit } from '@components';
import { useEffect, useState } from 'react';

type Props = { device: DeviceType };

export function Device(props: Props) {
    const { device } = props;
    const history = useHistory();
    const [tags, setTags] = useState<string[]>([]);

    useEffect(() => {
        if (device) {
            setTags(device.tags);
        } else {
            setTags([]);
        }
    }, [device]);

    const openDevice = (ip: string) => window.open(`http://${ip}`, '_blank');

    return (
        <div className={`${styles.component} m-5`}>
            <Card>
                <>
                    <div>Name: {device.name}</div>
                    <div className="flex items-center">
                        <div className="mr-3">IP: {device.ip}</div>
                        <FontAwesomeIcon
                            className="mr-3"
                            icon={faExternalLinkAlt}
                            onClick={() => openDevice(device.ip)}
                        />
                    </div>
                    <div>Type: {device.type}</div>
                    <div>State: {device.state}</div>
                    <div className="flex">
                        {tags.map((tag) => (
                            <Tag key={tag} label={tag} />
                        ))}
                    </div>

                    <ButtonEdit
                        onClick={() => history.push(`/devices/${device.id}`)}
                    />
                </>
            </Card>
        </div>
    );
}
