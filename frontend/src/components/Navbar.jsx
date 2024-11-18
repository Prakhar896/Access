import React from 'react'
import colouredLogo from '/logo/svg/logo-color.svg';
import { Button, Flex, Image, MenuIcon, Spacer } from '@chakra-ui/react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowRightFromBracket, faBars } from '@fortawesome/free-solid-svg-icons';

function Navbar() {
    return (
        <Flex as={"nav"} alignItems={"center"} rounded={"10px"} mb={"20px"} p={"10px"} m={"1rem"} overflow="hidden">
            <Button variant={"outline"} mr={"20px"}>
                <FontAwesomeIcon icon={faBars} />
            </Button>
            <Image src={colouredLogo} alt='Logo' maxH={'50px'} rounded={'xl'} />
            <Spacer />
            <Button variant={"ghost"}><FontAwesomeIcon icon={faArrowRightFromBracket} color='red' /></Button>
        </Flex>
    )
}

export default Navbar