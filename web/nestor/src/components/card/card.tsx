import styles from './card.module.css';

type Props = { children?: JSX.Element };

export function Card(props: Props) {
    const { children } = props;

    return (
        <div
            className="px-5 py-3 rounded-md shadow-md text-white"
            style={{ backgroundColor: '#364363' }}
        >
            {children}
        </div>
    );
}
