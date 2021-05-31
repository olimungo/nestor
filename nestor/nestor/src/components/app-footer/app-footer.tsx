import styles from './app-footer.module.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    faProjectDiagram,
    faTag,
    faNetworkWired,
    faSearch,
} from '@fortawesome/free-solid-svg-icons';
import { IconProp } from '@fortawesome/fontawesome-svg-core';
import { useHistory } from 'react-router-dom';

type Props = {};

type Section = {
    label: string;
    icon: IconProp;
    uri: string;
};

const sections: Section[] = [
    { label: 'COMMANDS', icon: faProjectDiagram, uri: '/commands' },
    { label: 'TAGS', icon: faTag, uri: '/tags' },
    { label: 'DEVICES', icon: faNetworkWired, uri: '/devices' },
    { label: 'SEARCH', icon: faSearch, uri: 'search' },
];

export function AppFooter(props: Props) {
    // const {} = props;
    const history = useHistory();

    return (
        <div className="text-white p-2" style={{ backgroundColor: '#29324c' }}>
            <nav>
                <ul className="flex justify-between">
                    {sections.map((section, index) => (
                        <div
                            key={index}
                            className="w-100 self-center flex justify-center "
                            onClick={() => history.push(section.uri)}
                        >
                            <li className="w-100">
                                <div
                                    className={`${styles.link} flex flex-col py-3 px-6 hover:bg-black hover:bg-opacity-20`}
                                >
                                    <FontAwesomeIcon
                                        className="self-center"
                                        icon={section.icon}
                                        size="2x"
                                    />

                                    <span className="self-center text-blue-300 mt-2 hidden sm:block">
                                        {section.label}
                                    </span>
                                </div>
                            </li>

                            {index < sections.length - 1 ? (
                                <li
                                    className="h-16 self-center"
                                    style={{
                                        borderWidth: '.05rem',
                                        borderColor: 'rgba(255,255,255,.07)',
                                    }}
                                ></li>
                            ) : (
                                ''
                            )}
                        </div>
                    ))}
                </ul>
            </nav>
        </div>
    );
}
