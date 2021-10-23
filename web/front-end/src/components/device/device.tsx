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
                <div className="m-2">
                    <div className="flex">
                        <div className="flex text-2xl">
                            <div>{device.type}</div>
                            <div className="mx-4">{device.netId}</div>
                            <div className="mx-2 text-gray-400">{device.state}</div>
                        </div>
                    </div>

                    <div className="inline-flex mt-2 py-1 px-2 rounded-md bg-gray-800 text-lg">
                        <div className="mr-3">{device.ip}</div>

                        <FontAwesomeIcon
                            className="mt-1"
                            icon={faExternalLinkAlt}
                            onClick={() => openDevice(device.ip)}
                        />
                    </div>

                    <div className="flex flex-wrap my-5">
                        {tags.map((tag) => (
                            <Tag key={tag} label={tag} />
                        ))}
                    </div>

                    <div className="flex justify-end">
                        <ButtonEdit onClick={() => onEditDevice(device.urlId)} />
                    </div>
                </div>
            </Card>
        </div>
    );
}
