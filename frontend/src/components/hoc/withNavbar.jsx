import Navbar from "../Navbar";

const withNavbar = (WrappedComponent) => {
    return (props) => {
        return <>
            <Navbar />
            <WrappedComponent {...props} />
        </>
    }
}

export default withNavbar;