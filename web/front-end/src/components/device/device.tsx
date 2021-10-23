import styles from './device.module.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExternalLinkAlt } from '@fortawesome/free-solid-svg-icons';
import { IotDevice } from '@models';
import { Card, Tag, ButtonEdit } from '@components';
import { useEffect, useState } from 'react';

type Props = { device: IotDevice; onEditDevice?: (urlId: string) => void };

export function Device(props: Props) {
    const dummyCallback = () => true;
    const { device, onEditDevice = dummyCallback } = props;
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
                    <div>Name: {device.id}</div>
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

                    <ButtonEdit onClick={() => onEditDevice(device.urlId)} />
                </>
            </Card>
        </div>
    );
}
