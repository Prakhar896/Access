import React, { useEffect, useState } from 'react'
import { Box, Button, Heading, Menu, MenuButton, MenuDivider, MenuItem, MenuItemOption, MenuList, MenuOptionGroup, Spacer, Spinner, Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr, useDisclosure, useMediaQuery, useToast } from '@chakra-ui/react';
import { Link as ChakraLink } from '@chakra-ui/react';
import { useSelector } from 'react-redux';
import server from '../../networking';
import configureShowToast from '../../components/showToast';
import CentredSpinner from '../../components/CentredSpinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowDown, faArrowUpFromBracket, faCircleDown } from '@fortawesome/free-solid-svg-icons';
import FilesList from '../../components/FilesList';
import UploadFilesModal from '../../components/UploadFilesModal';
import { BsChevronDown } from 'react-icons/bs';
import { useNavigate } from 'react-router-dom';

function Directory() {
    const { username, loaded } = useSelector(state => state.auth);
    const [showingVerifyEmailLink, setShowingVerifyEmailLink] = useState(false);
    const [filesData, setFilesData] = useState([]);
    const [retrievingFiles, setRetrievingFiles] = useState(true);
    const [sortBy, setSortBy] = useState(localStorage.getItem("UserPrefSortAttribute") || "name");
    const [sortOrder, setSortOrder] = useState(localStorage.getItem("UserPrefSortOrder") || "asc");
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const { isOpen: isUploadModalOpen, onOpen: onUploadModalOpen, onClose: onUploadModalClose } = useDisclosure();
    const toast = useToast();
    const showToast = configureShowToast(toast);
    const navigate = useNavigate();

    const processFileData = (data) => {
        var newData = [];
        for (var file of data) {
            file["originalLastUpdate"] = structuredClone(file["lastUpdate"]);
            file["originalUploadedTimestamp"] = structuredClone(file["uploadedTimestamp"]);

            file["lastUpdate"] = file["lastUpdate"] ? new Date(file["lastUpdate"]).toLocaleString() : null;
            file["uploadedTimestamp"] = new Date(file["uploadedTimestamp"]).toLocaleString();

            newData.push(file);
        }

        return newData;
    }

    const sortAndSetFiles = (data) => {
        localStorage.setItem("UserPrefSortAttribute", sortBy);
        localStorage.setItem("UserPrefSortOrder", sortOrder);

        var newData = [...data];
        if (data.length > 0) {
            newData.sort((a, b) => {
                if (!a[sortBy] || !b[sortBy]) {
                    return 0;
                } else if (sortOrder == "asc") {
                    return a[sortBy] > b[sortBy] ? 1 : -1;
                } else {
                    return a[sortBy] < b[sortBy] ? 1 : -1;
                }
            });
        }

        setFilesData(newData);
    }

    const fetchFiles = () => {
        server.get("/directory")
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "object" && !Array.isArray(res.data)) {
                        sortAndSetFiles(processFileData(Object.values(res.data)));
                        setRetrievingFiles(false);
                        return
                    } else {
                        console.log("Unexpected response format when retrieving files; response: ", res.data);
                    }
                } else {
                    console.log("Non-200 status code received in retrieving files; response: ", res.data);
                }
                showToast("Something went wrong", "Couldn't retrieves files. Please try again.", "error");
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in retrieving files; response: ", err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");

                        if (err.response.data == "UERROR: Verify your email first.") {
                            setShowingVerifyEmailLink(true);
                        }
                        return
                    } else {
                        console.log("Unknown response from server in retrieving files; response: ", err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log("Error occurred in retrieving files; message: ", err.message);
                } else {
                    console.log("Unknown error occurred in retrieving files; error: ", err);
                }
                showToast("Something went wrong", "Couldn't retrieves files. Please try again.", "error");
            })
    }

    useEffect(() => {
        if (loaded) {
            fetchFiles();
        }
    }, [loaded]);

    useEffect(() => {
        sortAndSetFiles(filesData);

        // if (!retrievingFiles) {
        //     // If not retrieving files, force a prop transfer update to FilesList by triggering a re-render with a timeout
        //     setRetrievingFiles(true);
        //     setTimeout(() => {
        //         setRetrievingFiles(false);
        //     }, 0)
        // }
    }, [sortBy, sortOrder]);

    return (
        <>
            <Box display={'flex'} flexDir={'column'} justifyContent={'left'} m={!limitedScreen ? '1rem' : '10px'} p={'10px'}>
                <Box display={'flex'} justifyContent={'left'} flexDirection={'row'} alignItems={'center'}>
                    <Heading as={'h1'} fontSize={'3xl'} fontFamily={'Ubuntu'}>My Files</Heading>
                    <Menu closeOnSelect={false}>
                        <MenuButton as={Button} variant={'Default'} rightIcon={<BsChevronDown />} ml={"10px"} size={'xs'}>
                            Sort by
                        </MenuButton>
                        <MenuList>
                            <MenuOptionGroup defaultValue={localStorage.getItem("UserPrefSortAttribute") || "name"} title='Attribute' type='radio'>
                                <MenuItemOption value='name' onClick={() => setSortBy('name')}>Name</MenuItemOption>
                                <MenuItemOption value='lastUpdate' onClick={() => setSortBy('lastUpdate')}>Last Modified</MenuItemOption>
                                <MenuItemOption value='uploadedTimestamp' onClick={() => setSortBy('uploadedTimestamp')}>Uploaded</MenuItemOption>
                            </MenuOptionGroup>
                            <MenuOptionGroup defaultValue={localStorage.getItem("UserPrefSortOrder") || "asc"} title='Order' type='radio'>
                                <MenuItemOption value='asc' onClick={() => setSortOrder('asc')}>Ascending</MenuItemOption>
                                <MenuItemOption value='desc' onClick={() => setSortOrder('desc')}>Descending</MenuItemOption>
                            </MenuOptionGroup>
                        </MenuList>
                    </Menu>
                    <Spacer />
                    <Button variant={'Default'} onClick={onUploadModalOpen}><FontAwesomeIcon icon={faArrowUpFromBracket} /></Button>
                </Box>
                {showingVerifyEmailLink ? (
                    <Button variant={'Default'} onClick={() => navigate("/portal/account")} mt={'20px'} maxW={'fit-content'}>Verify Email in My Account</Button>
                ) : (
                    <FilesList filesData={filesData} retrieving={retrievingFiles} triggerReload={fetchFiles} />
                )}
            </Box>
            <UploadFilesModal isOpen={isUploadModalOpen} onOpen={onUploadModalOpen} onClose={onUploadModalClose} triggerReload={fetchFiles} />
        </>
    )
}

export default Directory;