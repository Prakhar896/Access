import { Button, FormControl, FormHelperText, FormLabel, HStack, IconButton, Input, Menu, MenuButton, MenuDivider, MenuItem, MenuList, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Text, useDisclosure, useMediaQuery, useToast, VStack } from '@chakra-ui/react'
import { useState } from 'react'
import { BsFillInfoCircleFill, BsFillShareFill, BsPencilFill, BsTrash3Fill } from 'react-icons/bs'
import { FaDownload, FaEllipsisV, FaFileDownload, FaHamburger } from 'react-icons/fa'
import RenameFileModal from './fileManagement/RenameFileModal';
import DeleteFileModal from './fileManagement/DeleteFileModal';
import ShareFileModal from './fileManagement/ShareFileModal';

function FileActions({ fileData, downloadLinkFor, triggerReload }) {
    const { isOpen: infoModalOpen, onOpen: onInfoModalOpen, onClose: onInfoModalClose } = useDisclosure();
    const { isOpen: isShareModalOpen, onOpen: onShareModalOpen, onClose: onShareModalClose } = useDisclosure();
    const { isOpen: renameModalOpen, onOpen: onRenameModalOpen, onClose: onRenameModalClose } = useDisclosure();
    const { isOpen: isDeleteAlertOpen, onClose: onDeleteAlertClose, onOpen: onDeleteAlertOpen } = useDisclosure();
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const lastModifiedDate = fileData.originalLastUpdate ? new Date(fileData.originalLastUpdate) : null;
    const uploadedDate = fileData.originalUploadedTimestamp ? new Date(fileData.originalUploadedTimestamp) : null;

    const handleOpen = (open) => {
        onInfoModalClose();
        open();
    }

    const handleClose = (close) => {
        onInfoModalOpen();
        close();
    }

    function FileInfoModal() {
        return <Modal onClose={onInfoModalClose} isOpen={infoModalOpen} isCentered size={'sm'}>
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
                        <Text fontWeight={'bold'}>Actions</Text>
                        <Button variant={'Default'} leftIcon={<FaFileDownload />} onClick={() => location.href = downloadLinkFor(fileData.name)}>Download</Button>
                        <Button variant={'Default'} leftIcon={<BsFillShareFill />} onClick={() => handleOpen(onShareModalOpen)}>Sharing...</Button>
                        <Button variant={'Default'} leftIcon={<BsPencilFill />} onClick={() => handleOpen(onRenameModalOpen)}>Rename</Button>
                        <Button variant={'solid'} colorScheme={'red'} leftIcon={<BsTrash3Fill />} onClick={() => handleOpen(onDeleteAlertOpen)}>Delete</Button>
                    </VStack>
                </ModalBody>
                <ModalFooter>
                    <Button variant={'Default'} onClick={onInfoModalClose}>Done</Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    }

    if (limitedScreen) {
        return <>
            <IconButton icon={<FaEllipsisV />} variant={'ghost'} aria-label='Options' onClick={onInfoModalOpen} />
            <FileInfoModal />
            <ShareFileModal fileData={fileData} isShareModalOpen={isShareModalOpen} onShareModalOpen={onShareModalOpen} onShareModalClose={() => handleClose(onShareModalClose)} />
            <RenameFileModal fileData={fileData} renameModalOpen={renameModalOpen} onRenameModalOpen={onRenameModalOpen} onRenameModalClose={() => handleClose(onRenameModalClose)} triggerReload={triggerReload} />
            <DeleteFileModal fileData={fileData} isDeleteAlertOpen={isDeleteAlertOpen} onDeleteAlertOpen={onDeleteAlertOpen} onDeleteAlertClose={() => handleClose(onDeleteAlertClose)} triggerReload={triggerReload} />
        </>
    }

    return <Menu>
        <MenuButton
            as={IconButton}
            aria-label='Options'
            icon={<FaEllipsisV />}
            variant='ghost'
        />
        <MenuList>
            <MenuItem icon={<FaFileDownload />} onClick={() => location.href = downloadLinkFor(fileData.name)}>
                Download
            </MenuItem>
            <MenuItem icon={<BsFillShareFill />} onClick={onShareModalOpen}>Sharing...</MenuItem>
            <MenuItem icon={<BsPencilFill />} onClick={onRenameModalOpen}>Rename</MenuItem>
            <MenuDivider />
            <MenuItem color={'red'} icon={<BsTrash3Fill />} onClick={onDeleteAlertOpen}>Delete</MenuItem>

            <ShareFileModal fileData={fileData} isShareModalOpen={isShareModalOpen} onShareModalOpen={onShareModalOpen} onShareModalClose={onShareModalClose} />
            <RenameFileModal fileData={fileData} renameModalOpen={renameModalOpen} onRenameModalOpen={onRenameModalOpen} onRenameModalClose={onRenameModalClose} triggerReload={triggerReload} />
            <DeleteFileModal fileData={fileData} isDeleteAlertOpen={isDeleteAlertOpen} onDeleteAlertOpen={onDeleteAlertOpen} onDeleteAlertClose={onDeleteAlertClose} triggerReload={triggerReload} />
        </MenuList>
    </Menu>
}

export default FileActions