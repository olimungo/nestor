import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSlidersH } from '@fortawesome/free-solid-svg-icons';

type Props = {};

export function AppHeader(props: Props) {
    // const {} = props;

    return (
        <div
            className="bg-red-500 text-white px-7 py-3 flex justify-between items-center"
            style={{ backgroundColor: '#29324c' }}
        >
            <div className="flex">
                <span
                    className="text-4xl"
                    style={{ fontFamily: 'Roboto-Thin', fontWeight: 'bold' }}
                >
                    nestor
                </span>
                <div className="text-4xl w-2 h-2 rounded-full bg-red-500 relative top-6 left-1"></div>
            </div>

            <div>
                <FontAwesomeIcon className="" icon={faSlidersH} size="2x" />
            </div>
        </div>
    );
}
