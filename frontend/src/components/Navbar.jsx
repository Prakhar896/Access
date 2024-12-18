import React, { useEffect } from 'react'
import colouredLogo from '/logo/svg/logo-color.svg';
import { Button, Flex, Image, MenuIcon, Spacer, useDisclosure, useMediaQuery, useToast } from '@chakra-ui/react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowRightFromBracket, faBars } from '@fortawesome/free-solid-svg-icons';
import configureShowToast from './showToast';
import { useDispatch } from 'react-redux';
import { logout, setDisableSessionCheck } from '../slices/AuthState';
import { useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';

function Navbar() {
    const toast = useToast();
    const navigate = useNavigate();
    const showToast = configureShowToast(toast);
    const dispatch = useDispatch();
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const { isOpen, onOpen, onClose } = useDisclosure();

    const handleLogout = () => {
        dispatch(logout(true, (msg) => {
            if (typeof msg == "string" && msg.startsWith("SUCCESS")) {
                showToast("Logged out!", "See you soon!", "success");
                navigate('/');
            } else {
                showToast("Something went wrong", "Logout failed.", "error");
            }
        }))
    }

    return (
        <>
            <Flex as={"nav"} alignItems={"center"} rounded={"10px"} mb={"20px"} p={"10px"} m={!limitedScreen ? "1rem" : "10px"} overflow="hidden">
                <Button variant={"outline"} mr={"20px"} onClick={() => onOpen()}>
                    <FontAwesomeIcon icon={faBars} />
                </Button>
                <Image src={colouredLogo} alt='Logo' maxH={'50px'} rounded={'xl'} onClick={() => navigate('/portal/files')} />
                <Spacer />
                <Button variant={"ghost"} onClick={handleLogout}><FontAwesomeIcon icon={faArrowRightFromBracket} color='red' /></Button>
            </Flex>
            <Sidebar isOpen={isOpen} onClose={onClose} />
        </>
    )
}

export default Navbar