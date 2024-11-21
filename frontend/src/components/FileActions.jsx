import { Button, FormControl, FormHelperText, FormLabel, HStack, IconButton, Input, Menu, MenuButton, MenuDivider, MenuItem, MenuList, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Text, useDisclosure, useMediaQuery, useToast, VStack } from '@chakra-ui/react'
import { useState } from 'react'
import { BsFillInfoCircleFill, BsTrash3Fill } from 'react-icons/bs'
import { FaDownload, FaEllipsisV, FaFileDownload, FaHamburger } from 'react-icons/fa'
import RenameFile from './fileManagement/RenameFile';
import DeleteFile from './fileManagement/DeleteFile';
import ShareFile from './fileManagement/ShareFile';

function FileActions({ fileData, downloadLinkFor, triggerReload }) {
    const { isOpen: infoModalOpen, onOpen: onInfoModalOpen, onClose: onInfoModalClose } = useDisclosure();
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const lastModifiedDate = fileData.originalLastUpdate ? new Date(fileData.originalLastUpdate) : null;
    const uploadedDate = fileData.originalUploadedTimestamp ? new Date(fileData.originalUploadedTimestamp) : null;

    return (
        <>
            <Menu>
                <MenuButton
                    as={IconButton}
                    aria-label='Options'
                    icon={<FaEllipsisV />}
                    variant='ghost'
                />
                <MenuList>
                    {limitedScreen && (
                        <MenuItem icon={<BsFillInfoCircleFill />} onClick={onInfoModalOpen}>
                            Get Info
                        </MenuItem>
                    )}
                    <MenuItem icon={<FaFileDownload />} onClick={() => location.href = downloadLinkFor(fileData.name)}>
                        Download
                    </MenuItem>
                    <ShareFile fileData={fileData} />
                    <RenameFile fileData={fileData} triggerReload={triggerReload} />
                    <MenuDivider />
                    <DeleteFile fileData={fileData} triggerReload={triggerReload} />
                </MenuList>
            </Menu>

            <Modal onClose={onInfoModalClose} isOpen={infoModalOpen} isCentered size={'sm'}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader fontSize={'md'}>{fileData.name}</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <VStack spacing={"10px"} alignItems={"flex-start"}>
                            <Text fontWeight={'bold'}>Name</Text>
                            <Text>{fileData.name}</Text>
                            <Text fontWeight={'bold'}>Last modified</Text>
                            <Text>{lastModifiedDate ? lastModifiedDate.toLocaleString('en-GB', { dateStyle: "long", timeStyle: "medium", hour12: true }) : "Unavailable"}</Text>
                            <Text fontWeight={'bold'}>Uploaded</Text>
                            <Text>{uploadedDate ? uploadedDate.toLocaleString('en-GB', { dateStyle: "long", timeStyle: "medium", hour12: true }) : "Unavailable"}</Text>
                        </VStack>
                    </ModalBody>
                    <ModalFooter>
                        <Button variant={'Default'} onClick={onInfoModalClose}>Got it</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default FileActions