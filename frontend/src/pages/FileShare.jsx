import { Box, Button, ButtonGroup, FormControl, FormLabel, Heading, Image, Input, ScaleFade, Slide, Spacer, Spinner, Text, useColorMode, useMediaQuery, VStack } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import colouredLogo from '/logo/svg/logo-color.svg';
import server from '../networking';

function FileShare() {
    const backendURL = server.defaults.baseURL;
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const [searchParams] = useSearchParams();
    const [code, setCode] = useState(searchParams.get('code') || '');

    const [sharingInfo, setSharingInfo] = useState({});
    const [errorMessage, setErrorMessage] = useState("");
    const [gettingSharingInfo, setGettingSharingInfo] = useState(false);

    const [password, setPassword] = useState("");

    const handleFieldEnter = (e) => { if (e.key === 'Enter') { accessFile(); } }
    const handlePasswordChange = (e) => { setPassword(e.target.value); }

    const getSharingInfo = async () => {
        if (!code) {
            setErrorMessage("Invalid share link.");
            return;
        }

        setGettingSharingInfo(true);
        server.post("/sharing/info", {
            linkCode: code
        })
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "object" && !Array.isArray(res.data)) {
                        setSharingInfo(res.data);
                        setGettingSharingInfo(false);
                        return;
                    } else {
                        console.log(`Unexpected response in retrieving sharing info for file ${code}; response:`, res.data);
                    }
                } else {
                    console.log(`Non-200 status code in getting sharing info for file ${code}; response:`, res.data);
                }

                showToast("Something went wrong", "Couldn't get sharing information. Please try again.", "error");
                setGettingSharingInfo(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log(`User error occurred in retrieving file sharing info for file ${code}; response:`, err.response.data);
                        setErrorMessage(err.response.data.substring("UERROR: ".length));
                        setGettingSharingInfo(false);
                        return;
                    } else {
                        console.log(`Error occurred in retrieving file sharing info for file ${code}; response:`, err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log(`Error occurred in retrieving file sharing info for file ${code}; error:`, err.message);
                } else {
                    console.log(`Unknown error occurred in retrieving file sharing info for file ${code}; error:`, err);
                }

                setErrorMessage("An error occurred while trying to get sharing information. Please try again.");
                setGettingSharingInfo(false);
            })
    }

    const accessFile = () => {
        location.href = `${backendURL}/sharing/get/${sharingInfo.linkCode}?password=${password}`;
    }

    useEffect(() => {
        if (code) {
            getSharingInfo();
        } else {
            setErrorMessage("Invalid share link.");
        }
    }, [])

    return (
        <Box display={'flex'} flexDirection={'column'} justifyContent={'center'} maxW={'100%'} p={!limitedScreen ? '10px' : '0px'}>
            <Box display={'flex'} flexDirection={'column'} justifyContent={'space-between'} alignItems={'center'} mt={'10%'} mb={"20px"}>
                <Spacer />
                <Link to={'/'}>
                    <Image src={colouredLogo} alt={'Logo'} maxH={'100px'} rounded={'xl'} />
                </Link>
                <Spacer />
                <Box display={'flex'} flexDir={'column'} justifyContent={'left'} alignItems={'center'} maxW={limitedScreen ? '70%' : '50%'} p={!limitedScreen ? '10px' : '0px'} mt={limitedScreen ? '20px' : '0px'}>
                    <ScaleFade in={true} initialScale={0.9}>
                        <Box display={'flex'} flexDir={'column'} alignItems={'center'}>
                            <Heading as={'h1'} size={'xl'}>Shared File</Heading>
                            <VStack spacing={"20px"} alignItems={"flex-start"} w={'100%'}>
                                {errorMessage && <Text color={'red'} mt={"20px"}>{errorMessage}</Text>}
                                {!gettingSharingInfo && !errorMessage && (
                                    <>
                                        <Text mt={"20px"}><strong>{sharingInfo.owner}</strong> is sharing <strong>{sharingInfo.name}</strong> with you.</Text>
                                        {sharingInfo.passwordRequired && (
                                            <>
                                                <Text fontWeight={'bold'} mt={"20px"}>This file is password protected.</Text>
                                                <FormControl id='password' required>
                                                    <FormLabel>Enter password</FormLabel>
                                                    <Input onKeyUp={handleFieldEnter} type='password' value={password} onChange={handlePasswordChange} required />
                                                </FormControl>
                                            </>
                                        )}
                                    </>
                                )}
                            </VStack>
                            <Button variant={(errorMessage || !sharingInfo || (sharingInfo.passwordRequired && !password)) ? 'solid' : 'Default'} w={{ base: 'xs', md: 'md', lg: 'lg' }} mt={"30px"} onClick={accessFile} isDisabled={errorMessage || !sharingInfo || (sharingInfo.passwordRequired && !password)} isLoading={gettingSharingInfo}>Access</Button>
                        </Box>
                    </ScaleFade>
                </Box>
                <Spacer />
            </Box>
        </Box>
    )
}

export default FileShare